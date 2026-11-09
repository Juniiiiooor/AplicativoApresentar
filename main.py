"""Lançador do Quiz Arena a partir da raiz do projeto.

Permite subir o backend Flask com um comando simples:

    python main.py

O código real da API fica em `backend/main.py`. Este arquivo apenas carrega
esse módulo e inicia o servidor, para que a dica mostrada na web funcione
sem precisar entrar na pasta `backend`.

Variáveis de ambiente opcionais:
    HOST  (padrão: 127.0.0.1)
    PORT  (padrão: 8000)
"""

from __future__ import annotations

import importlib.util
import os
import sys
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

    print(f"Quiz Arena API (Flask) em http://{host}:{porta}")
    print(f"Documentação: http://{host}:{porta}/docs")
    print("Pressione CTRL+C para parar.\n")

    app.run(host=host, port=porta, debug=True)
