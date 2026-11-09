"""Modo arcade do Quiz Arena (Pygame).

Uso (a partir da raiz do projeto):
    python arcade/quiz_arcade.py

O modo arcade reaproveita as mesmas perguntas e a mesma pontuação do núcleo
(`core/`). Ele é uma alternativa visual ao quiz web, pensada para a
apresentação no telão.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

import pygame

from core.storage import RepositorioJSON

LARGURA, ALTURA = 960, 640

COR_FUNDO = (15, 23, 42)
COR_PAINEL = (30, 41, 59)
COR_TEXTO = (226, 232, 240)
COR_FRACO = (148, 163, 184)
COR_DESTAQUE = (56, 189, 248)
COR_SUCESSO = (34, 197, 94)
COR_ERRO = (248, 113, 113)

LETRAS = "ABCD"
ATALHOS = {
    pygame.K_1: 0,
    pygame.K_2: 1,
    pygame.K_3: 2,
    pygame.K_4: 3,
    pygame.K_a: 0,
    pygame.K_b: 1,
    pygame.K_c: 2,
    pygame.K_d: 3,
}


class ArcadeQuiz:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Quiz Arena · Modo Arcade")
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        self.relogio = pygame.time.Clock()

        self.fonte_titulo = pygame.font.SysFont("segoeui", 32, bold=True)
        self.fonte_pergunta = pygame.font.SysFont("segoeui", 24, bold=True)
        self.fonte = pygame.font.SysFont("segoeui", 19)
        self.fonte_pequena = pygame.font.SysFont("segoeui", 15)

        self.repo = RepositorioJSON()
        self.perguntas = self.repo.carregar_perguntas()
        random.shuffle(self.perguntas)

        self.indice = 0
        self.pontuacao = 0
        self.acertos = 0
        self.resposta: int | None = None
        self.pontos_ultima = 0
        self.momento_resposta = 0
        self.inicio_pergunta = pygame.time.get_ticks()
        self.finalizado = False
        self.rodando = True
        self.pergunta = self.perguntas[0] if self.perguntas else None
        self.tempo_limite = self.pergunta.tempo_limite if self.pergunta else 20

    # ------------------------------------------------------------- utilidades
    def _quebrar_texto(self, texto: str, fonte, largura: int) -> list[str]:
        palavras = texto.split()
        linhas: list[str] = []
        atual = ""
        for palavra in palavras:
            teste = f"{atual} {palavra}".strip()
            if fonte.size(teste)[0] <= largura:
                atual = teste
            else:
                if atual:
                    linhas.append(atual)
                atual = palavra
        if atual:
            linhas.append(atual)
        return linhas

    def _tempo_restante(self) -> int:
        if self.resposta is not None or not self.pergunta:
            return 0
        decorrido = (pygame.time.get_ticks() - self.inicio_pergunta) / 1000
        return max(0, self.tempo_limite - int(decorrido))

    # ---------------------------------------------------------------- partida
    def _responder(self, alternativa: int) -> None:
        if self.resposta is not None or not self.pergunta:
            return

        tempo = self._tempo_restante()
        self.resposta = alternativa
        self.momento_resposta = pygame.time.get_ticks()

        if alternativa == self.pergunta.correta:
            self.acertos += 1
            self.pontos_ultima = self.pergunta.pontos(alternativa, tempo)
            self.pontuacao += self.pontos_ultima
        else:
            self.pontos_ultima = 0

    def _proxima(self) -> None:
        self.indice += 1
        self.resposta = None
        self.pontos_ultima = 0

        if self.indice >= len(self.perguntas):
            self.finalizado = True
            self.pergunta = None
            return

        self.pergunta = self.perguntas[self.indice]
        self.tempo_limite = self.pergunta.tempo_limite
        self.inicio_pergunta = pygame.time.get_ticks()

    def _reiniciar(self) -> None:
        random.shuffle(self.perguntas)
        self.indice = 0
        self.pontuacao = 0
        self.acertos = 0
        self.resposta = None
        self.pontos_ultima = 0
        self.finalizado = False
        self.pergunta = self.perguntas[0] if self.perguntas else None
        self.tempo_limite = self.pergunta.tempo_limite if self.pergunta else 20
        self.inicio_pergunta = pygame.time.get_ticks()

    # ---------------------------------------------------------------- desenho
    def _desenhar(self) -> None:
        self.tela.fill(COR_FUNDO)

        titulo = self.fonte_titulo.render("Quiz Arena · Arcade", True, COR_DESTAQUE)
        self.tela.blit(titulo, (40, 24))

        placar = self.fonte.render(
            f"Pontos: {self.pontuacao}  ·  Acertos: {self.acertos}",
            True,
            COR_TEXTO,
        )
        self.tela.blit(placar, (LARGURA - placar.get_width() - 40, 34))

        if self.finalizado:
            self._desenhar_fim()
            pygame.display.flip()
            return

        if not self.pergunta:
            dica = self.fonte.render(
                "Nenhuma pergunta cadastrada em data/perguntas.json.",
                True,
                COR_ERRO,
            )
            self.tela.blit(dica, (60, 220))
            pygame.display.flip()
            return

        tempo = self._tempo_restante()
        pygame.draw.rect(
            self.tela, COR_PAINEL, (40, 92, LARGURA - 80, 16), border_radius=8
        )
        proporcao = tempo / max(1, self.pergunta.tempo_limite)
        cor_tempo = COR_ERRO if tempo <= 5 else COR_DESTAQUE
        pygame.draw.rect(
            self.tela,
            cor_tempo,
            (40, 92, int((LARGURA - 80) * proporcao), 16),
            border_radius=8,
        )
        texto_tempo = self.fonte_pequena.render(f"{tempo}s", True, COR_TEXTO)
        self.tela.blit(texto_tempo, (LARGURA - 78, 66))

        linhas = self._quebrar_texto(
            self.pergunta.enunciado, self.fonte_pergunta, LARGURA - 120
        )
        y = 140
        for linha in linhas:
            superficie = self.fonte_pergunta.render(linha, True, COR_TEXTO)
            self.tela.blit(superficie, (60, y))
            y += 36

        y += 16
        for indice, alternativa in enumerate(self.pergunta.alternativas[:4]):
            caixa = pygame.Rect(60, y, LARGURA - 120, 58)
            cor_borda = COR_PAINEL
            cor_fundo = COR_PAINEL

            if self.resposta is not None:
                if indice == self.pergunta.correta:
                    cor_borda, cor_fundo = COR_SUCESSO, (20, 83, 45)
                elif indice == self.resposta:
                    cor_borda, cor_fundo = COR_ERRO, (127, 29, 29)

            pygame.draw.rect(self.tela, cor_fundo, caixa, border_radius=12)
            pygame.draw.rect(self.tela, cor_borda, caixa, width=2, border_radius=12)

            texto = self.fonte.render(
                f"{LETRAS[indice]}) {alternativa}", True, COR_TEXTO
            )
            self.tela.blit(texto, (caixa.x + 18, caixa.y + 17))
            y += 70

        if self.resposta is not None:
            if self.resposta == self.pergunta.correta:
                mensagem = f"✅ Correto! +{self.pontos_ultima} pontos"
                cor = COR_SUCESSO
            elif self.resposta == -1:
                mensagem = "⏰ Tempo esgotado!"
                cor = COR_ERRO
            else:
                mensagem = "❌ Resposta errada!"
                cor = COR_ERRO

            superficie = self.fonte.render(mensagem, True, cor)
            self.tela.blit(superficie, (60, y + 2))

            if self.pergunta.explicacao:
                explicacao = self.fonte_pequena.render(
                    self.pergunta.explicacao[:110], True, COR_DESTAQUE
                )
                self.tela.blit(explicacao, (60, y + 30))

            dica = self.fonte_pequena.render(
                "Enter/Espaço para avançar agora", True, COR_FRACO
            )
            self.tela.blit(dica, (LARGURA - dica.get_width() - 60, y + 30))
        else:
            dica = self.fonte_pequena.render(
                "Pressione 1-4 ou A-D para responder", True, COR_FRACO
            )
            self.tela.blit(dica, (60, y + 2))

        pygame.display.flip()

    def _desenhar_fim(self) -> None:
        mensagem = self.fonte_titulo.render("Fim de jogo!", True, COR_DESTAQUE)
        self.tela.blit(mensagem, (LARGURA // 2 - mensagem.get_width() // 2, 220))

        resumo = self.fonte.render(
            f"{self.pontuacao} pontos · {self.acertos} acerto(s)", True, COR_TEXTO
        )
        self.tela.blit(resumo, (LARGURA // 2 - resumo.get_width() // 2, 280))

        dica = self.fonte.render(
            "R para jogar novamente · ESC para sair", True, COR_FRACO
        )
        self.tela.blit(dica, (LARGURA // 2 - dica.get_width() // 2, 340))

    # ------------------------------------------------------------------ loop
    def executar(self) -> None:
        while self.rodando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.rodando = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_ESCAPE:
                        self.rodando = False
                    elif self.finalizado and evento.key == pygame.K_r:
                        self._reiniciar()
                    elif not self.finalizado and self.resposta is None:
                        if evento.key in ATALHOS:
                            self._responder(ATALHOS[evento.key])
                    elif not self.finalizado and self.resposta is not None:
                        if evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                            self._proxima()

            if not self.finalizado and self.pergunta:
                if self.resposta is None and self._tempo_restante() <= 0:
                    self._responder(-1)
                elif (
                    self.resposta is not None
                    and pygame.time.get_ticks() - self.momento_resposta > 2500
                ):
                    self._proxima()

            self._desenhar()
            self.relogio.tick(30)

        pygame.quit()


def main() -> None:
    ArcadeQuiz().executar()


if __name__ == "__main__":
    main()
