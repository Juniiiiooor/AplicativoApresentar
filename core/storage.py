"""Persistência simples em JSON.

O grupo pode trocar esta camada por SQLite no futuro sem mudar as regras
do jogo: basta manter os mesmos métodos públicos.
"""

from __future__ import annotations

import json
import os
import sys
import threading
from pathlib import Path
from typing import Any

from .models import Desafio, Jogador, Pergunta

RAIZ_PROJETO = Path(__file__).resolve().parent.parent


def _diretorio_dados_padrao() -> Path:
    """Pasta de dados gravável.

    Na execução normal usa ``data/`` na raiz do projeto. No executável
    empacotado (PyInstaller) usa ``data/`` ao lado do .exe, para que o
    ranking continue salvo entre uma execução e outra.
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "data"
    return RAIZ_PROJETO / "data"


DIR_DADOS_PADRAO = _diretorio_dados_padrao()


class RepositorioJSON:
    def __init__(self, data_dir: str | Path | None = None) -> None:
        pasta = data_dir or os.getenv("QUIZ_DATA_DIR") or DIR_DADOS_PADRAO
        self.data_dir = Path(pasta)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.arquivo_perguntas = self.data_dir / "perguntas.json"
        self.arquivo_desafios = self.data_dir / "desafios.json"
        self.arquivo_ranking = self.data_dir / "ranking.json"
        self._lock = threading.Lock()
        self._garantir_arquivos()

    def _garantir_arquivos(self) -> None:
        for arquivo in (
            self.arquivo_perguntas,
            self.arquivo_desafios,
            self.arquivo_ranking,
        ):
            if not arquivo.exists():
                arquivo.write_text("[]", encoding="utf-8")

    def _ler(self, caminho: Path, padrao: Any) -> Any:
        try:
            return json.loads(caminho.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return padrao

    def _escrever(self, caminho: Path, dados: Any) -> None:
        temporario = caminho.with_suffix(caminho.suffix + ".tmp")
        temporario.write_text(
            json.dumps(dados, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporario.replace(caminho)

    # ----------------------------- Perguntas -----------------------------
    def carregar_perguntas(self) -> list[Pergunta]:
        dados = self._ler(self.arquivo_perguntas, [])
        return [Pergunta.de_dict(item) for item in dados if isinstance(item, dict)]

    def salvar_perguntas(self, perguntas: list[Pergunta]) -> None:
        self._escrever(
            self.arquivo_perguntas,
            [pergunta.para_dict() for pergunta in perguntas],
        )

    def adicionar_pergunta(self, pergunta: Pergunta) -> Pergunta:
        with self._lock:
            perguntas = self.carregar_perguntas()
            if any(item.id == pergunta.id for item in perguntas):
                raise ValueError("Já existe uma pergunta com esse id.")
            perguntas.append(pergunta)
            self.salvar_perguntas(perguntas)
            return pergunta

    # ------------------------------ Desafios -----------------------------
    def carregar_desafios(self) -> list[Desafio]:
        dados = self._ler(self.arquivo_desafios, [])
        return [Desafio.de_dict(item) for item in dados if isinstance(item, dict)]

    def salvar_desafios(self, desafios: list[Desafio]) -> None:
        self._escrever(
            self.arquivo_desafios,
            [desafio.para_dict() for desafio in desafios],
        )

    def adicionar_desafio(self, desafio: Desafio) -> Desafio:
        with self._lock:
            desafios = self.carregar_desafios()
            if any(item.id == desafio.id for item in desafios):
                raise ValueError("Já existe um desafio com esse id.")
            desafios.append(desafio)
            self.salvar_desafios(desafios)
            return desafio

    # ------------------------------ Ranking ------------------------------
    def carregar_ranking(self) -> list[dict[str, Any]]:
        dados = self._ler(self.arquivo_ranking, [])
        return dados if isinstance(dados, list) else []

    def salvar_ranking(self, ranking: list[dict[str, Any]]) -> None:
        self._escrever(self.arquivo_ranking, ranking)

    @staticmethod
    def _chave_ranking(item: dict[str, Any]) -> tuple[int, float, int]:
        return (
            int(item.get("pontuacao", 0)),
            float(item.get("aproveitamento", 0)),
            int(item.get("acertos", 0)),
        )

    def registrar_no_ranking(self, jogador: Jogador) -> list[dict[str, Any]]:
        """Guarda a melhor partida de cada jogador, sem duplicar nomes."""
        with self._lock:
            ranking = self.carregar_ranking()
            chave_nome = jogador.nome.strip().casefold()
            novo = jogador.para_dict()

            existente = next(
                (
                    item
                    for item in ranking
                    if str(item.get("nome", "")).strip().casefold() == chave_nome
                ),
                None,
            )

            if existente is None:
                novo["partidas"] = 1
                ranking.append(novo)
            else:
                existente["partidas"] = int(existente.get("partidas", 1)) + 1
                if self._chave_ranking(novo) > self._chave_ranking(existente):
                    partidas = existente["partidas"]
                    existente.clear()
                    existente.update(novo)
                    existente["partidas"] = partidas

            ranking.sort(key=self._chave_ranking, reverse=True)
            self.salvar_ranking(ranking)
            return ranking

    def top_ranking(self, limite: int = 10) -> list[dict[str, Any]]:
        ranking = self.carregar_ranking()
        ranking.sort(key=self._chave_ranking, reverse=True)
        return ranking[: max(1, limite)]
