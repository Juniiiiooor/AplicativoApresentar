"""API do Quiz Arena (Flask).

Execute a partir da pasta backend:
    python main.py
ou:
    flask --app main run --debug --port 8000

Documentação simples: http://localhost:8000/docs
Health check: http://localhost:8000/health
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from flask import Flask, jsonify, request, send_from_directory

from core.models import CATEGORIAS_PADRAO, DIFICULDADES, ConflitoDeResposta
from core.services import QuizService

app = Flask(__name__)
app.json.ensure_ascii = False
service = QuizService()

# Front-end React compilado. Quando existe, o próprio Flask entrega o app web,
# então `python main.py` sobe tudo em uma única porta/processo.
DIST_WEB = RAIZ_PROJETO / "web" / "dist"

ORIGENS_PADRAO = "http://localhost:5173,http://127.0.0.1:5173"


def _origens_permitidas() -> list[str]:
    valor = os.getenv("QUIZ_CORS_ORIGINS", ORIGENS_PADRAO)
    return [item.strip() for item in valor.split(",") if item.strip()]


@app.after_request
def adicionar_cabecalhos_cors(resposta):
    """CORS sem depender de extensão externa."""
    origem = request.headers.get("Origin")
    permitidas = _origens_permitidas()

    if "*" in permitidas:
        resposta.headers["Access-Control-Allow-Origin"] = "*"
    elif origem and origem in permitidas:
        resposta.headers["Access-Control-Allow-Origin"] = origem
        resposta.headers["Vary"] = "Origin"

    resposta.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    resposta.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Admin-Token"
    return resposta


@app.route("/api/<path:_caminho>", methods=["OPTIONS"])
def preflight(_caminho: str):
    return "", 204


def _erro(mensagem: str, status: int):
    return jsonify({"detail": mensagem}), status


def _corpo_json() -> dict[str, Any]:
    dados = request.get_json(silent=True)
    return dados if isinstance(dados, dict) else {}


def _validar_admin():
    token = os.getenv("QUIZ_ADMIN_TOKEN")
    if not token:
        return None
    if request.headers.get("X-Admin-Token", "") != token:
        return _erro("Token de administrador inválido.", 401)
    return None


def _inteiro(valor: Any) -> bool:
    return isinstance(valor, int) and not isinstance(valor, bool)


def _numero(valor: Any) -> bool:
    return isinstance(valor, (int, float)) and not isinstance(valor, bool)


@app.get("/health")
def healthcheck():
    return jsonify(
        {
            "status": "ok",
            "service": "quiz-arena",
            "framework": "flask",
        }
    )


@app.get("/docs")
def documentacao():
    rotas = [
        ("GET", "/health", "Verifica se a API está no ar"),
        ("GET", "/api/categorias", "Lista as categorias disponíveis"),
        ("GET", "/api/perguntas", "Lista perguntas sem revelar a correta"),
        ("POST", "/api/perguntas", "Cadastra uma pergunta (opcionalmente com token)"),
        ("GET", "/api/desafios", "Lista os desafios do Caça ao Bug"),
        ("POST", "/api/desafios", "Cadastra um desafio (opcionalmente com token)"),
        ("POST", "/api/desafios/{id}/responder", "Corrige uma resposta do Caça ao Bug"),
        ("POST", "/api/partidas", "Inicia uma partida"),
        ("GET", "/api/partidas/{id}", "Consulta o estado da partida"),
        ("POST", "/api/partidas/{id}/responder", "Responde a pergunta atual"),
        ("GET", "/api/ranking?limite=10", "Retorna o ranking"),
    ]
    linhas = "".join(
        f"<tr><td><code>{metodo}</code></td><td><code>{rota}</code></td>"
        f"<td>{descricao}</td></tr>"
        for metodo, rota, descricao in rotas
    )
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Quiz Arena API</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #0f172a; color: #e2e8f0; }}
    h1 {{ color: #38bdf8; }}
    table {{ border-collapse: collapse; width: 100%; max-width: 900px; }}
    td, th {{ border-bottom: 1px solid #334155; padding: .6rem; text-align: left; }}
    code {{ background: #1e293b; padding: .15rem .35rem; border-radius: .3rem; }}
  </style>
</head>
<body>
  <h1>🎯 Quiz Arena API</h1>
  <p>Backend em Flask. As rotas abaixo devolvem JSON.</p>
  <table>
    <thead><tr><th>Método</th><th>Rota</th><th>Descrição</th></tr></thead>
    <tbody>{linhas}</tbody>
  </table>
</body>
</html>"""


@app.get("/api/categorias")
def listar_categorias():
    perguntas = service.listar_perguntas(publico=True)
    existentes = {pergunta["categoria"] for pergunta in perguntas}
    return jsonify(sorted(set(CATEGORIAS_PADRAO) | existentes))


@app.get("/api/perguntas")
def listar_perguntas():
    categoria = request.args.get("categoria")
    return jsonify(service.listar_perguntas(categoria=categoria, publico=True))


@app.post("/api/perguntas")
def criar_pergunta():
    bloqueio = _validar_admin()
    if bloqueio:
        return bloqueio

    dados = _corpo_json()

    enunciado = dados.get("enunciado")
    if not isinstance(enunciado, str) or len(enunciado.strip()) < 5:
        return _erro("O enunciado precisa ter pelo menos 5 caracteres.", 422)

    alternativas = dados.get("alternativas")
    if not isinstance(alternativas, list) or len(alternativas) < 2:
        return _erro("A pergunta precisa de pelo menos 2 alternativas.", 422)
    if not all(isinstance(item, str) and item.strip() for item in alternativas):
        return _erro("Todas as alternativas precisam ser textos não vazios.", 422)

    correta = dados.get("correta")
    if not _inteiro(correta):
        return _erro("O índice da alternativa correta precisa ser um inteiro.", 422)
    if not 0 <= correta < len(alternativas):
        return _erro("O índice da alternativa correta é inválido.", 400)

    dificuldade = dados.get("dificuldade", "facil")
    if dificuldade not in DIFICULDADES:
        return _erro("Dificuldade inválida. Use facil, medio ou dificil.", 422)

    tempo_limite = dados.get("tempo_limite", 20)
    if not _inteiro(tempo_limite) or tempo_limite <= 0:
        return _erro("O tempo limite deve ser um inteiro maior que zero.", 422)

    categoria = dados.get("categoria", "Geral")
    if not isinstance(categoria, str) or not categoria.strip():
        return _erro("A categoria precisa ser um texto não vazio.", 422)

    explicacao = dados.get("explicacao", "")
    if not isinstance(explicacao, str):
        return _erro("A explicação precisa ser um texto.", 422)

    try:
        pergunta = service.criar_pergunta(
            {
                "enunciado": enunciado,
                "alternativas": alternativas,
                "correta": correta,
                "categoria": categoria.strip(),
                "dificuldade": dificuldade,
                "tempo_limite": tempo_limite,
                "explicacao": explicacao,
            }
        )
    except ValueError as erro:
        return _erro(str(erro), 400)

    return jsonify(pergunta.para_dict()), 201


@app.get("/api/desafios")
def listar_desafios():
    return jsonify(service.listar_desafios(publico=True))


@app.get("/api/desafios/<desafio_id>")
def obter_desafio(desafio_id: str):
    try:
        desafio = service.obter_desafio(desafio_id)
    except KeyError:
        return _erro("Desafio não encontrado.", 404)
    return jsonify(desafio.para_publico())


@app.post("/api/desafios")
def criar_desafio():
    bloqueio = _validar_admin()
    if bloqueio:
        return bloqueio

    dados = _corpo_json()

    titulo = dados.get("titulo")
    if not isinstance(titulo, str) or len(titulo.strip()) < 3:
        return _erro("O título precisa ter pelo menos 3 caracteres.", 422)

    codigo = dados.get("codigo")
    if not isinstance(codigo, str) or not codigo.strip():
        return _erro("O trecho de código é obrigatório.", 422)

    descricao = dados.get("descricao")
    if not isinstance(descricao, str) or len(descricao.strip()) < 5:
        return _erro("A descrição precisa ter pelo menos 5 caracteres.", 422)

    alternativas = dados.get("alternativas")
    if not isinstance(alternativas, list) or len(alternativas) < 2:
        return _erro("O desafio precisa de pelo menos 2 alternativas.", 422)
    if not all(isinstance(item, str) and item.strip() for item in alternativas):
        return _erro("Todas as alternativas precisam ser textos não vazios.", 422)

    correta = dados.get("correta")
    if not _inteiro(correta):
        return _erro("O índice da alternativa correta precisa ser um inteiro.", 422)
    if not 0 <= correta < len(alternativas):
        return _erro("O índice da alternativa correta é inválido.", 400)

    linguagem = dados.get("linguagem", "Código")
    if not isinstance(linguagem, str) or not linguagem.strip():
        return _erro("A linguagem precisa ser um texto não vazio.", 422)

    tema = dados.get("tema", "Geral")
    if not isinstance(tema, str) or not tema.strip():
        return _erro("O tema precisa ser um texto não vazio.", 422)

    explicacao = dados.get("explicacao", "")
    if not isinstance(explicacao, str):
        return _erro("A explicação precisa ser um texto.", 422)

    try:
        desafio = service.criar_desafio(
            {
                "titulo": titulo,
                "linguagem": linguagem.strip(),
                "tema": tema.strip(),
                "codigo": codigo,
                "descricao": descricao,
                "alternativas": alternativas,
                "correta": correta,
                "explicacao": explicacao,
            }
        )
    except ValueError as erro:
        return _erro(str(erro), 400)

    return jsonify(desafio.para_dict()), 201


@app.post("/api/desafios/<desafio_id>/responder")
def responder_desafio(desafio_id: str):
    dados = _corpo_json()

    alternativa = dados.get("alternativa")
    if not _inteiro(alternativa) or alternativa < 0:
        return _erro("A alternativa precisa ser um inteiro maior ou igual a zero.", 422)

    try:
        desafio, correta, pontos = service.responder_desafio(desafio_id, alternativa)
    except KeyError:
        return _erro("Desafio não encontrado.", 404)
    except ValueError as erro:
        return _erro(str(erro), 400)

    return jsonify(
        {
            "correta": correta,
            "alternativa_escolhida": alternativa,
            "alternativa_correta": desafio.correta,
            "pontos": pontos,
            "explicacao": desafio.explicacao,
            "desafio": desafio.para_publico(revelar=True),
        }
    )


@app.post("/api/partidas")
def iniciar_partida():
    dados = _corpo_json()

    nome = dados.get("nome")
    if not isinstance(nome, str) or not 2 <= len(nome.strip()) <= 30:
        return _erro("O nome precisa ter entre 2 e 30 caracteres.", 422)

    quantidade = dados.get("quantidade")
    if quantidade is not None and (not _inteiro(quantidade) or quantidade < 1):
        return _erro("A quantidade precisa ser um inteiro maior ou igual a 1.", 422)

    categoria = dados.get("categoria")
    if categoria is not None and not isinstance(categoria, str):
        return _erro("A categoria precisa ser um texto.", 422)

    dificuldade = dados.get("dificuldade")
    if dificuldade is not None and dificuldade not in DIFICULDADES:
        return _erro("Dificuldade inválida. Use facil, medio ou dificil.", 422)

    try:
        partida = service.iniciar_partida(
            nome=nome.strip(),
            quantidade=quantidade,
            categoria=categoria,
            dificuldade=dificuldade,
        )
    except ValueError as erro:
        return _erro(str(erro), 400)

    return jsonify(partida.para_publico()), 201


@app.get("/api/partidas/<partida_id>")
def obter_partida(partida_id: str):
    try:
        partida = service.obter_partida(partida_id)
    except KeyError:
        return _erro("Partida não encontrada.", 404)
    return jsonify(partida.para_publico())


@app.post("/api/partidas/<partida_id>/responder")
def responder(partida_id: str):
    dados = _corpo_json()

    alternativa = dados.get("alternativa")
    if not _inteiro(alternativa) or alternativa < -1:
        return _erro("A alternativa precisa ser um inteiro maior ou igual a -1.", 422)

    tempo_restante = dados.get("tempo_restante")
    if tempo_restante is not None and (
        not _numero(tempo_restante) or tempo_restante < 0
    ):
        return _erro("O tempo restante precisa ser um número maior ou igual a zero.", 422)

    pergunta_id = dados.get("pergunta_id")
    if pergunta_id is not None and not isinstance(pergunta_id, str):
        return _erro("O pergunta_id precisa ser um texto.", 422)

    try:
        partida, pergunta, resposta = service.responder(
            partida_id=partida_id,
            alternativa=alternativa,
            tempo_restante=tempo_restante,
            pergunta_id=pergunta_id,
        )
    except KeyError:
        return _erro("Partida não encontrada.", 404)
    except ConflitoDeResposta as erro:
        return _erro(str(erro), 409)
    except ValueError as erro:
        return _erro(str(erro), 400)

    return jsonify(
        {
            "correta": resposta.correta,
            "alternativa_escolhida": alternativa,
            "alternativa_correta": pergunta.correta,
            "pontos": resposta.pontos,
            "explicacao": pergunta.explicacao,
            "pergunta_respondida": pergunta.para_publico(revelar=True),
            "partida": partida.para_publico(),
        }
    )


@app.get("/api/ranking")
def ranking():
    limite_bruto = request.args.get("limite", "10")
    try:
        limite = int(limite_bruto)
    except (TypeError, ValueError):
        return _erro("O limite precisa ser um inteiro.", 422)

    return jsonify(service.ranking(limite=max(1, min(limite, 100))))


@app.get("/")
@app.get("/<path:caminho>")
def servir_web(caminho: str = ""):
    """Entrega o front-end React compilado (`web/dist`) junto com a API.

    Dessa forma `python main.py` abre a web completa em
    http://127.0.0.1:8000 sem precisar de um segundo servidor (Vite). Rotas de
    API inexistentes continuam respondendo JSON 404.
    """
    if caminho == "api" or caminho.startswith("api/"):
        return _erro("Rota não encontrada.", 404)

    if DIST_WEB.is_dir():
        raiz_dist = DIST_WEB.resolve()
        alvo = (DIST_WEB / caminho).resolve()
        dentro = alvo == raiz_dist or raiz_dist in alvo.parents

        if caminho and dentro and alvo.is_file():
            return send_from_directory(DIST_WEB, caminho)

        # Um arquivo com extensão que não existe deve ser 404 (ex.: favicon).
        if caminho and "." in Path(caminho).name:
            return _erro("Arquivo não encontrado.", 404)

        if (DIST_WEB / "index.html").is_file():
            return send_from_directory(DIST_WEB, "index.html")

    return _erro(
        "Front-end não compilado. Rode 'npm install' e 'npm run build' dentro de web/.",
        404,
    )


if __name__ == "__main__":
    porta = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "127.0.0.1")
    # use_reloader=False mantém um único processo: fechar o terminal encerra o
    # servidor de verdade (o reloader deixava um processo filho na porta 8000).
    app.run(host=host, port=porta, debug=False, use_reloader=False)
