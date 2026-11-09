"""Lançador do Quiz Arena a partir da raiz do projeto.

Com um único comando:

    python main.py

sobe a API Flask **e** entrega o front-end React compilado (`web/dist`) na
mesma porta. Ou seja, a web só funciona enquanto este processo estiver aberto.
Ao fechar o terminal (ou pressionar CTRL+C), tudo é encerrado.

O código real da API fica em `backend/main.py`. Este arquivo apenas carrega
esse módulo e inicia o servidor, para que a dica mostrada na web funcione
sem precisar entrar na pasta `backend`.

Variáveis de ambiente opcionais:
    HOST                 (padrão: 127.0.0.1)
    PORT                 (padrão: 8000)
    QUIZ_ABRIR_NAVEGADOR (padrão: 1; use 0 para não abrir o navegador)
    QUIZ_DEBUG           (padrão: 0; use 1 para modo de depuração)
"""

from __future__ import annotations

import importlib.util
import os
import sys
import threading
import webbrowser
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
BACKEND = RAIZ / "backend"

# Garante que `core` (raiz) e `backend` sejam importáveis de qualquer pasta.
for caminho in (str(RAIZ), str(BACKEND)):
    if caminho not in sys.path:
        sys.path.insert(0, caminho)


def carregar_app():
    """Carrega o app Flask de backend/main.py sem depender do nome do módulo."""
    arquivo = BACKEND / "main.py"
    if not arquivo.exists():
        raise SystemExit(
            f"Não encontrei {arquivo}. Rode este comando na raiz do projeto."
        )

    spec = importlib.util.spec_from_file_location("quiz_arena_api", arquivo)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Não foi possível carregar {arquivo}.")

    modulo = importlib.util.module_from_spec(spec)
    sys.modules["quiz_arena_api"] = modulo
    spec.loader.exec_module(modulo)
    return modulo.app


app = carregar_app()


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    porta = int(os.getenv("PORT", "8000"))
    url = f"http://{host}:{porta}"

    print(f"Quiz Arena em {url}")
    print(f"Documentação da API: {url}/docs")
    print("Pressione CTRL+C (ou feche esta janela) para parar.\n")

    if os.getenv("QUIZ_ABRIR_NAVEGADOR", "1") != "0":
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    # use_reloader=False = um único processo. Assim, ao fechar o terminal, o
    # servidor realmente para (o reloader do Flask deixava um processo filho
    # segurando a porta 8000 depois de encerrar).
    app.run(
        host=host,
        port=porta,
        debug=os.getenv("QUIZ_DEBUG", "0") == "1",
        use_reloader=False,
    )
