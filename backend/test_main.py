"""Testes da API do Quiz Arena (Flask)."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TMP = Path(tempfile.mkdtemp(prefix="quiz-arena-test-"))
shutil.copy(RAIZ / "data" / "perguntas.json", TMP / "perguntas.json")
os.environ["QUIZ_DATA_DIR"] = str(TMP)

from main import app  # noqa: E402

client = app.test_client()


def test_healthcheck() -> None:
    resposta = client.get("/health")
    assert resposta.status_code == 200
    corpo = resposta.get_json()
    assert corpo["status"] == "ok"
    assert corpo["framework"] == "flask"


def test_documentacao() -> None:
    resposta = client.get("/docs")
    assert resposta.status_code == 200
    assert "Quiz Arena API" in resposta.get_data(as_text=True)


def test_listar_perguntas_nao_revela_resposta() -> None:
    resposta = client.get("/api/perguntas")
    assert resposta.status_code == 200
    perguntas = resposta.get_json()
    assert len(perguntas) >= 1
    assert all("correta" not in pergunta for pergunta in perguntas)


def test_criar_pergunta() -> None:
    payload = {
        "enunciado": "Qual é a capital do Brasil?",
        "alternativas": ["Rio de Janeiro", "Brasília", "São Paulo", "Salvador"],
        "correta": 1,
        "categoria": "Geral",
        "dificuldade": "facil",
        "tempo_limite": 20,
        "explicacao": "Brasília foi inaugurada como capital em 1960.",
    }
    resposta = client.post("/api/perguntas", json=payload)
    assert resposta.status_code == 201
    assert resposta.get_json()["enunciado"] == payload["enunciado"]


def test_criar_pergunta_invalida() -> None:
    resposta = client.post(
        "/api/perguntas",
        json={
            "enunciado": "Oi",
            "alternativas": ["A", "B"],
            "correta": 0,
        },
    )
    assert resposta.status_code == 422

    resposta = client.post(
        "/api/perguntas",
        json={
            "enunciado": "Pergunta válida?",
            "alternativas": ["A", "B"],
            "correta": 9,
        },
    )
    assert resposta.status_code == 400


def test_partida_completa() -> None:
    resposta = client.post("/api/partidas", json={"nome": "Teste", "quantidade": 2})
    assert resposta.status_code == 201
    partida = resposta.get_json()
    assert partida["status"] == "em_andamento"
    assert partida["pergunta_atual"] is not None

    partida_id = partida["id"]

    primeira = client.post(
        f"/api/partidas/{partida_id}/responder",
        json={
            "alternativa": 0,
            "pergunta_id": partida["pergunta_atual"]["id"],
        },
    )
    assert primeira.status_code == 200
    assert "correta" in primeira.get_json()
    assert "alternativa_correta" in primeira.get_json()

    segunda = client.post(
        f"/api/partidas/{partida_id}/responder",
        json={
            "alternativa": 1,
            "pergunta_id": primeira.get_json()["partida"]["pergunta_atual"]["id"],
        },
    )
    assert segunda.status_code == 200
    assert segunda.get_json()["partida"]["status"] == "finalizada"
    assert "revisao" in segunda.get_json()["partida"]


def test_resposta_repetida_retorna_409() -> None:
    inicio = client.post("/api/partidas", json={"nome": "Idempotente", "quantidade": 2})
    partida = inicio.get_json()
    pergunta_id = partida["pergunta_atual"]["id"]

    primeira = client.post(
        f"/api/partidas/{partida['id']}/responder",
        json={"alternativa": 0, "pergunta_id": pergunta_id},
    )
    assert primeira.status_code == 200

    repetida = client.post(
        f"/api/partidas/{partida['id']}/responder",
        json={"alternativa": 0, "pergunta_id": pergunta_id},
    )
    assert repetida.status_code == 409


def test_explicacao_aparece_so_depois_de_responder() -> None:
    client.post(
        "/api/perguntas",
        json={
            "enunciado": "Pergunta com explicação para o teste?",
            "alternativas": ["Certa", "Errada"],
            "correta": 0,
            "categoria": "Explicacao",
            "dificuldade": "facil",
            "tempo_limite": 20,
            "explicacao": "Esta é a explicação.",
        },
    )

    inicio = client.post(
        "/api/partidas",
        json={"nome": "Explicado", "categoria": "Explicacao", "quantidade": 1},
    )
    partida = inicio.get_json()
    assert "explicacao" not in partida["pergunta_atual"]

    resposta = client.post(
        f"/api/partidas/{partida['id']}/responder",
        json={"alternativa": 0, "pergunta_id": partida["pergunta_atual"]["id"]},
    )
    assert resposta.status_code == 200
    assert resposta.get_json()["explicacao"] == "Esta é a explicação."


def test_filtro_por_dificuldade() -> None:
    resposta = client.post(
        "/api/partidas",
        json={"nome": "Dificil", "dificuldade": "dificil", "quantidade": 1},
    )
    assert resposta.status_code == 201
    assert resposta.get_json()["pergunta_atual"]["dificuldade"] == "dificil"


def test_nome_curto_retorna_422() -> None:
    resposta = client.post("/api/partidas", json={"nome": "A"})
    assert resposta.status_code == 422


def test_partida_inexistente_retorna_404() -> None:
    assert client.get("/api/partidas/nao-existe").status_code == 404


def test_ranking() -> None:
    resposta = client.get("/api/ranking")
    assert resposta.status_code == 200
    assert isinstance(resposta.get_json(), list)
