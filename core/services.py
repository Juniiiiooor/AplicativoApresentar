"""Serviços que orquestram as regras do jogo.

O backend Flask e o painel Tkinter usam esta mesma classe.
"""

from __future__ import annotations

import random
from typing import Any

from .models import Desafio, Jogador, Partida, Pergunta
from .storage import RepositorioJSON

MAX_PARTIDAS_EM_MEMORIA = 200


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

    # ------------------------------ Desafios -----------------------------
    def listar_desafios(
        self,
        publico: bool = True,
    ) -> list[dict[str, Any]] | list[Desafio]:
        desafios = self.repo.carregar_desafios()
        if publico:
            return [desafio.para_publico() for desafio in desafios]
        return desafios

    def criar_desafio(self, dados: dict[str, Any] | Desafio) -> Desafio:
        desafio = dados if isinstance(dados, Desafio) else Desafio.de_dict(dados)
        return self.repo.adicionar_desafio(desafio)

    def obter_desafio(self, desafio_id: str) -> Desafio:
        for desafio in self.repo.carregar_desafios():
            if desafio.id == desafio_id:
                return desafio
        raise KeyError("Desafio não encontrado.")

    def responder_desafio(
        self,
        desafio_id: str,
        alternativa: int,
    ) -> tuple[Desafio, bool, int]:
        desafio = self.obter_desafio(desafio_id)
        if not 0 <= alternativa < len(desafio.alternativas):
            raise ValueError("Alternativa inválida.")

        correta = desafio.esta_correta(alternativa)
        return desafio, correta, desafio.pontos(alternativa)

    # ------------------------------ Partidas -----------------------------
    def iniciar_partida(
        self,
        nome: str,
        quantidade: int | None = None,
        categoria: str | None = None,
        dificuldade: str | None = None,
        embaralhar: bool = True,
    ) -> Partida:
        perguntas = self.repo.carregar_perguntas()

        if categoria:
            perguntas = [
                pergunta
                for pergunta in perguntas
                if pergunta.categoria.lower() == categoria.lower()
            ]

        if dificuldade:
            perguntas = [
                pergunta
                for pergunta in perguntas
                if pergunta.dificuldade.lower() == dificuldade.lower()
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
        self._limpar_partidas()
        return partida

    def _limpar_partidas(self) -> None:
        """Evita crescimento infinito da memória em partidas longas."""
        excedente = len(self.partidas) - MAX_PARTIDAS_EM_MEMORIA
        if excedente <= 0:
            return

        finalizadas = [
            partida_id
            for partida_id, partida in self.partidas.items()
            if partida.status == "finalizada"
        ]
        for partida_id in finalizadas[:excedente]:
            self.partidas.pop(partida_id, None)

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
        pergunta_id: str | None = None,
    ) -> tuple[Partida, Pergunta, Any]:
        partida = self.obter_partida(partida_id)
        pergunta = partida.pergunta_atual()

        if pergunta is None:
            raise ValueError("A partida já terminou.")

        resposta = partida.responder(alternativa, tempo_restante, pergunta_id)

        if partida.status == "finalizada":
            self.repo.registrar_no_ranking(partida.jogador)

        return partida, pergunta, resposta

    # ------------------------------ Ranking ------------------------------
    def ranking(self, limite: int = 10) -> list[dict[str, Any]]:
        return self.repo.top_ranking(limite)
