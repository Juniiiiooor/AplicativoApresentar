"""Núcleo do Quiz Arena (regras + persistência)."""

from .models import (
    CATEGORIAS_PADRAO,
    DIFICULDADES,
    Jogador,
    Partida,
    Pergunta,
    Resposta,
)
from .services import QuizService
from .storage import RepositorioJSON

__all__ = [
    "CATEGORIAS_PADRAO",
    "DIFICULDADES",
    "Jogador",
    "Partida",
    "Pergunta",
    "Resposta",
    "QuizService",
    "RepositorioJSON",
]
