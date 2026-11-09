"""Modelos de domínio do Quiz Arena.

Aqui ficam as regras do jogo, sem depender de Tkinter, FastAPI ou React.
Assim o mesmo núcleo é usado pelo painel desktop, pelo backend e pelos testes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

DIFICULDADES = {"facil": 1, "medio": 2, "dificil": 3}
CATEGORIAS_PADRAO = (
    "Geral",
    "Web",
    "Python",
    "POO",
    "React",
    "Backend",
    "Git",
    "Games",
)


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat()


class ConflitoDeResposta(ValueError):
    """A resposta não corresponde à pergunta atual (provável reenvio)."""


@dataclass
class Pergunta:
    """Uma pergunta do quiz e suas alternativas."""

    id: str
    enunciado: str
    alternativas: list[str]
    correta: int
    categoria: str = "Geral"
    dificuldade: str = "facil"
    tempo_limite: int = 20
    explicacao: str = ""

    def __post_init__(self) -> None:
        self.enunciado = self.enunciado.strip()
        self.alternativas = [alternativa.strip() for alternativa in self.alternativas]
        self.explicacao = self.explicacao.strip()

        if len(self.enunciado) < 5:
            raise ValueError("O enunciado precisa ter pelo menos 5 caracteres.")
        if len(self.alternativas) < 2:
            raise ValueError("A pergunta precisa de pelo menos 2 alternativas.")
        if not 0 <= self.correta < len(self.alternativas):
            raise ValueError("O índice da alternativa correta é inválido.")
        if self.dificuldade not in DIFICULDADES:
            raise ValueError(f"Dificuldade inválida: {self.dificuldade}")
        if self.tempo_limite <= 0:
            raise ValueError("O tempo limite deve ser maior que zero.")

    def esta_correta(self, alternativa: int) -> bool:
        return alternativa == self.correta

    def pontos(self, alternativa: int, tempo_restante: float | None = None) -> int:
        """Calcula a pontuação: base pela dificuldade + bônus de tempo."""
        if not self.esta_correta(alternativa):
            return 0

        base = 10 * DIFICULDADES[self.dificuldade]
        bonus = 0
        if tempo_restante is not None:
            bonus = max(0, min(5, int(tempo_restante)))
        return base + bonus

    def para_publico(self, revelar: bool = False) -> dict[str, Any]:
        """Versão sem a resposta correta, segura para enviar ao jogador.

        Use ``revelar=True`` somente depois que a pergunta já foi respondida,
        para incluir a explicação pedagógica.
        """
        dados = {
            "id": self.id,
            "enunciado": self.enunciado,
            "alternativas": list(self.alternativas),
            "categoria": self.categoria,
            "dificuldade": self.dificuldade,
            "tempo_limite": self.tempo_limite,
        }
        if revelar and self.explicacao:
            dados["explicacao"] = self.explicacao
        return dados

    def para_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "enunciado": self.enunciado,
            "alternativas": list(self.alternativas),
            "correta": self.correta,
            "categoria": self.categoria,
            "dificuldade": self.dificuldade,
            "tempo_limite": self.tempo_limite,
            "explicacao": self.explicacao,
        }

    @classmethod
    def de_dict(cls, dados: dict[str, Any]) -> "Pergunta":
        return cls(
            id=str(dados.get("id") or uuid4().hex[:8]),
            enunciado=dados["enunciado"],
            alternativas=list(dados["alternativas"]),
            correta=int(dados["correta"]),
            categoria=dados.get("categoria", "Geral"),
            dificuldade=dados.get("dificuldade", "facil"),
            tempo_limite=int(dados.get("tempo_limite", 20)),
            explicacao=str(dados.get("explicacao") or ""),
        )


@dataclass
class Jogador:
    """Representa quem está jogando e acumula a pontuação da partida."""

    nome: str
    id: str = field(default_factory=lambda: uuid4().hex[:8])
    pontuacao: int = 0
    acertos: int = 0
    respondidas: int = 0
    criado_em: str = field(default_factory=_agora)

    def __post_init__(self) -> None:
        self.nome = self.nome.strip()
        if len(self.nome) < 2:
            raise ValueError("O nome do jogador precisa ter pelo menos 2 caracteres.")

    @property
    def aproveitamento(self) -> float:
        if self.respondidas == 0:
            return 0.0
        return round(self.acertos / self.respondidas * 100, 1)

    def registrar_resposta(self, correta: bool, pontos: int) -> None:
        self.respondidas += 1
        if correta:
            self.acertos += 1
            self.pontuacao += pontos

    def para_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "nome": self.nome,
            "pontuacao": self.pontuacao,
            "acertos": self.acertos,
            "respondidas": self.respondidas,
            "aproveitamento": self.aproveitamento,
            "criado_em": self.criado_em,
        }

    @classmethod
    def de_dict(cls, dados: dict[str, Any]) -> "Jogador":
        jogador = cls(nome=dados["nome"], id=str(dados.get("id") or uuid4().hex[:8]))
        jogador.pontuacao = int(dados.get("pontuacao", 0))
        jogador.acertos = int(dados.get("acertos", 0))
        jogador.respondidas = int(dados.get("respondidas", 0))
        jogador.criado_em = str(dados.get("criado_em") or _agora())
        return jogador


@dataclass
class Resposta:
    """Registro de uma resposta dada pelo jogador."""

    pergunta_id: str
    alternativa: int
    correta: bool
    pontos: int
    tempo_restante: float | None = None

    def para_dict(self) -> dict[str, Any]:
        return {
            "pergunta_id": self.pergunta_id,
            "alternativa": self.alternativa,
            "correta": self.correta,
            "pontos": self.pontos,
            "tempo_restante": self.tempo_restante,
        }


@dataclass
class Partida:
    """Uma partida: jogador + sequência de perguntas + respostas."""

    jogador: Jogador
    perguntas: list[Pergunta]
    id: str = field(default_factory=lambda: uuid4().hex[:8])
    respostas: list[Resposta] = field(default_factory=list)
    indice_atual: int = 0
    status: str = "aguardando"  # aguardando | em_andamento | finalizada
    criada_em: str = field(default_factory=_agora)
    iniciada_em: str | None = None
    pergunta_iniciada_em: str | None = None
    finalizada_em: str | None = None

    def __post_init__(self) -> None:
        if not self.perguntas:
            raise ValueError("A partida precisa de pelo menos uma pergunta.")

    def iniciar(self) -> "Partida":
        if self.status == "finalizada":
            raise ValueError("Esta partida já foi finalizada.")
        self.status = "em_andamento"
        self.iniciada_em = _agora()
        self.pergunta_iniciada_em = self.iniciada_em
        return self

    def pergunta_atual(self) -> Pergunta | None:
        if self.status != "em_andamento" or self.indice_atual >= len(self.perguntas):
            return None
        return self.perguntas[self.indice_atual]

    def tempo_restante_servidor(self) -> float:
        """Calcula o tempo restante no servidor, sem confiar no cliente."""
        pergunta = self.pergunta_atual()
        if pergunta is None:
            return 0.0

        if not self.pergunta_iniciada_em:
            return float(pergunta.tempo_limite)

        try:
            inicio = datetime.fromisoformat(self.pergunta_iniciada_em)
        except ValueError:
            return float(pergunta.tempo_limite)

        decorrido = (datetime.now(timezone.utc) - inicio).total_seconds()
        return max(0.0, min(float(pergunta.tempo_limite), pergunta.tempo_limite - decorrido))

    def responder(
        self,
        alternativa: int,
        tempo_restante: float | None = None,
        pergunta_id: str | None = None,
    ) -> Resposta:
        """Registra uma resposta. Use alternativa=-1 quando o tempo esgotar.

        O bônus de tempo é calculado no servidor. ``tempo_restante`` é aceito
        apenas por compatibilidade e usado quando a partida não tem relógio.
        """
        if self.status != "em_andamento":
            raise ValueError("A partida não está em andamento.")

        pergunta = self.pergunta_atual()
        if pergunta is None:
            raise ValueError("Não há pergunta disponível.")
        if pergunta_id is not None and pergunta_id != pergunta.id:
            raise ConflitoDeResposta(
                "Esta pergunta já foi respondida ou não é mais a pergunta atual."
            )
        if alternativa != -1 and not 0 <= alternativa < len(pergunta.alternativas):
            raise ValueError("Alternativa inválida.")

        tempo_efetivo = self.tempo_restante_servidor()
        if not self.pergunta_iniciada_em and tempo_restante is not None:
            tempo_efetivo = tempo_restante

        correta = pergunta.esta_correta(alternativa)
        pontos = pergunta.pontos(alternativa, tempo_efetivo)
        resposta = Resposta(
            pergunta_id=pergunta.id,
            alternativa=alternativa,
            correta=correta,
            pontos=pontos,
            tempo_restante=round(tempo_efetivo, 1),
        )

        self.respostas.append(resposta)
        self.jogador.registrar_resposta(correta, pontos)
        self.indice_atual += 1

        if self.indice_atual >= len(self.perguntas):
            self.finalizar()
            self.pergunta_iniciada_em = None
        else:
            self.pergunta_iniciada_em = _agora()

        return resposta

    def finalizar(self) -> None:
        if self.status != "finalizada":
            self.status = "finalizada"
            self.finalizada_em = _agora()

    @property
    def total_perguntas(self) -> int:
        return len(self.perguntas)

    @property
    def progresso(self) -> str:
        return f"{min(self.indice_atual, self.total_perguntas)}/{self.total_perguntas}"

    @property
    def numero_pergunta(self) -> int:
        if self.status == "finalizada":
            return self.total_perguntas
        return min(self.indice_atual + 1, self.total_perguntas)

    def revisao(self) -> list[dict[str, Any]]:
        """Detalha cada resposta para a tela de resultado."""
        itens: list[dict[str, Any]] = []
        for resposta, pergunta in zip(self.respostas, self.perguntas):
            escolhida = (
                pergunta.alternativas[resposta.alternativa]
                if 0 <= resposta.alternativa < len(pergunta.alternativas)
                else None
            )
            itens.append(
                {
                    "pergunta_id": pergunta.id,
                    "enunciado": pergunta.enunciado,
                    "escolhida": escolhida,
                    "correta": pergunta.alternativas[pergunta.correta],
                    "acertou": resposta.correta,
                    "pontos": resposta.pontos,
                    "explicacao": pergunta.explicacao,
                }
            )
        return itens

    def resumo(self) -> dict[str, Any]:
        return {
            "jogador": self.jogador.para_dict(),
            "total_perguntas": self.total_perguntas,
            "respondidas": len(self.respostas),
            "acertos": self.jogador.acertos,
            "pontuacao": self.jogador.pontuacao,
            "aproveitamento": self.jogador.aproveitamento,
            "status": self.status,
        }

    def para_publico(self) -> dict[str, Any]:
        pergunta = self.pergunta_atual()
        dados = {
            "id": self.id,
            "status": self.status,
            "progresso": self.progresso,
            "indice_atual": self.indice_atual,
            "numero_pergunta": self.numero_pergunta,
            "total_perguntas": self.total_perguntas,
            "jogador": self.jogador.para_dict(),
            "pergunta_atual": pergunta.para_publico() if pergunta else None,
            "criada_em": self.criada_em,
            "iniciada_em": self.iniciada_em,
            "finalizada_em": self.finalizada_em,
        }
        if self.status == "finalizada":
            dados["revisao"] = self.revisao()
        return dados
