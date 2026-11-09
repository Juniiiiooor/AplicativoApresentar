"""API do Quiz Arena (FastAPI).

Execute a partir da pasta backend:
    uvicorn main:app --reload --port 8000

Documentação interativa: http://localhost:8000/docs
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.models import CATEGORIAS_PADRAO
from core.services import QuizService

app = FastAPI(
    title="Quiz Arena API",
    version="0.1.0",
    description="API de perguntas, partidas e ranking do Quiz Arena.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = QuizService()


class NovaPergunta(BaseModel):
    enunciado: str = Field(..., min_length=5)
    alternativas: list[str] = Field(..., min_length=2)
    correta: int = Field(..., ge=0)
    categoria: str = "Geral"
    dificuldade: Literal["facil", "medio", "dificil"] = "facil"
    tempo_limite: int = Field(20, gt=0)


class IniciarPartida(BaseModel):
    nome: str = Field(..., min_length=2, max_length=30)
    quantidade: int | None = Field(None, ge=1)
    categoria: str | None = None


class RespostaPayload(BaseModel):
    # -1 significa "o tempo esgotou" e conta como resposta errada.
    alternativa: int = Field(..., ge=-1)
    tempo_restante: float | None = Field(None, ge=0)


@app.get("/health")
def healthcheck() -> dict:
    return {"status": "ok", "service": "quiz-arena"}


@app.get("/api/categorias")
def listar_categorias() -> list[str]:
    perguntas = service.listar_perguntas(publico=True)
    existentes = {pergunta["categoria"] for pergunta in perguntas}
    return sorted(set(CATEGORIAS_PADRAO) | existentes)


@app.get("/api/perguntas")
def listar_perguntas(categoria: str | None = None) -> list[dict]:
    return service.listar_perguntas(categoria=categoria, publico=True)


@app.post("/api/perguntas", status_code=201)
def criar_pergunta(payload: NovaPergunta) -> dict:
    try:
        pergunta = service.criar_pergunta(payload.model_dump())
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro
    return pergunta.para_dict()


@app.post("/api/partidas", status_code=201)
def iniciar_partida(payload: IniciarPartida) -> dict:
    try:
        partida = service.iniciar_partida(
            nome=payload.nome,
            quantidade=payload.quantidade,
            categoria=payload.categoria,
        )
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro
    return partida.para_publico()


@app.get("/api/partidas/{partida_id}")
def obter_partida(partida_id: str) -> dict:
    try:
        partida = service.obter_partida(partida_id)
    except KeyError as erro:
        raise HTTPException(status_code=404, detail=str(erro)) from erro
    return partida.para_publico()


@app.post("/api/partidas/{partida_id}/responder")
def responder(partida_id: str, payload: RespostaPayload) -> dict:
    try:
        partida, pergunta, resposta = service.responder(
            partida_id=partida_id,
            alternativa=payload.alternativa,
            tempo_restante=payload.tempo_restante,
        )
    except KeyError as erro:
        raise HTTPException(status_code=404, detail=str(erro)) from erro
    except ValueError as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro

    return {
        "correta": resposta.correta,
        "alternativa_escolhida": payload.alternativa,
        "alternativa_correta": pergunta.correta,
        "pontos": resposta.pontos,
        "pergunta_respondida": pergunta.para_publico(),
        "partida": partida.para_publico(),
    }


@app.get("/api/ranking")
def ranking(limite: int = 10) -> list[dict]:
    return service.ranking(limite=max(1, min(limite, 100)))
