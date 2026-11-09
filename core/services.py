"""Serviços que orquestram as regras do jogo.

O backend FastAPI e o painel Tkinter usam esta mesma classe.
"""

from __future__ import annotations

import random
from typing import Any

from .models import Jogador, Partida, Pergunta
from .storage import RepositorioJSON


class QuizService:
    def __init__(self, repositorio: RepositorioJSON | None = None) -> None:
        self.repo = repositorio or RepositorioJSON()
        self.partidas: dict[str, Partida] = {}

    # ----------------------------- Perguntas -----------------------------
    def listar_perguntas(
        self,
        categoria: str | None = None,
        publico: bool = True,
    ) -> list[dict[str, Any]] | list[Pergunta]:
        perguntas = self.repo.carregar_perguntas()

        if categoria:
            perguntas = [
                pergunta
                for pergunta in perguntas
                if pergunta.categoria.lower() == categoria.lower()
            ]

        if publico:
            return [pergunta.para_publico() for pergunta in perguntas]
        return perguntas

    def criar_pergunta(self, dados: dict[str, Any] | Pergunta) -> Pergunta:
        pergunta = dados if isinstance(dados, Pergunta) else Pergunta.de_dict(dados)
        return self.repo.adicionar_pergunta(pergunta)

    # ------------------------------ Partidas -----------------------------
    def iniciar_partida(
        self,
        nome: str,
        quantidade: int | None = None,
        categoria: str | None = None,
        embaralhar: bool = True,
    ) -> Partida:
        perguntas = self.repo.carregar_perguntas()

        if categoria:
            perguntas = [
                pergunta
                for pergunta in perguntas
                if pergunta.categoria.lower() == categoria.lower()
            ]

        if not perguntas:
            raise ValueError("Nenhuma pergunta disponível para iniciar a partida.")

        if embaralhar:
            random.shuffle(perguntas)

        if quantidade:
            perguntas = perguntas[: max(1, int(quantidade))]

        jogador = Jogador(nome=nome)
        partida = Partida(jogador=jogador, perguntas=perguntas).iniciar()
        self.partidas[partida.id] = partida
        return partida

    def obter_partida(self, partida_id: str) -> Partida:
        partida = self.partidas.get(partida_id)
        if partida is None:
            raise KeyError("Partida não encontrada.")
        return partida

    def responder(
        self,
        partida_id: str,
        alternativa: int,
        tempo_restante: float | None = None,
    ) -> tuple[Partida, Pergunta, Any]:
        partida = self.obter_partida(partida_id)
        pergunta = partida.pergunta_atual()

        if pergunta is None:
            raise ValueError("A partida já terminou.")

        resposta = partida.responder(alternativa, tempo_restante)

        if partida.status == "finalizada":
            self.repo.registrar_no_ranking(partida.jogador)

        return partida, pergunta, resposta

    # ------------------------------ Ranking ------------------------------
    def ranking(self, limite: int = 10) -> list[dict[str, Any]]:
        return self.repo.top_ranking(limite)
