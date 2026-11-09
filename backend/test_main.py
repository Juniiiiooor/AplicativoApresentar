"""Testes da API do Quiz Arena."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TMP = Path(tempfile.mkdtemp(prefix="quiz-arena-test-"))
shutil.copy(RAIZ / "data" / "perguntas.json", TMP / "perguntas.json")
os.environ["QUIZ_DATA_DIR"] = str(TMP)

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def test_healthcheck() -> None:
    resposta = client.get("/health")
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "ok"


def test_listar_perguntas_nao_revela_resposta() -> None:
    resposta = client.get("/api/perguntas")
    assert resposta.status_code == 200
    perguntas = resposta.json()
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
    }
    resposta = client.post("/api/perguntas", json=payload)
    assert resposta.status_code == 201
    assert resposta.json()["enunciado"] == payload["enunciado"]


def test_partida_completa() -> None:
    resposta = client.post("/api/partidas", json={"nome": "Teste", "quantidade": 2})
    assert resposta.status_code == 201
    partida = resposta.json()
    assert partida["status"] == "em_andamento"
    assert partida["pergunta_atual"] is not None

    partida_id = partida["id"]

    primeira = client.post(
        f"/api/partidas/{partida_id}/responder",
        json={"alternativa": 0},
    )
    assert primeira.status_code == 200
    assert "correta" in primeira.json()
    assert "alternativa_correta" in primeira.json()

    segunda = client.post(
        f"/api/partidas/{partida_id}/responder",
        json={"alternativa": 1},
    )
    assert segunda.status_code == 200
    assert segunda.json()["partida"]["status"] == "finalizada"


def test_ranking() -> None:
    resposta = client.get("/api/ranking")
    assert resposta.status_code == 200
    assert isinstance(resposta.json(), list)
