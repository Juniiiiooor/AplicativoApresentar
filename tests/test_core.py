"""Testes do núcleo do Quiz Arena.

Usa apenas a biblioteca padrão (unittest), então roda sem instalar nada:
    python -m unittest discover -s tests -v
"""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from core.models import Jogador, Partida, Pergunta
from core.services import QuizService
from core.storage import RepositorioJSON


def criar_pergunta(
    dificuldade: str = "facil",
    correta: int = 0,
    tempo_limite: int = 20,
) -> Pergunta:
    return Pergunta(
        id="q-teste",
        enunciado="Qual é a resposta correta?",
        alternativas=["Certa", "Errada 1", "Errada 2", "Errada 3"],
        correta=correta,
        categoria="Geral",
        dificuldade=dificuldade,
        tempo_limite=tempo_limite,
    )


class TestPergunta(unittest.TestCase):
    def test_cria_pergunta_valida(self) -> None:
        pergunta = criar_pergunta()
        self.assertEqual(pergunta.enunciado, "Qual é a resposta correta?")
        self.assertEqual(len(pergunta.alternativas), 4)

    def test_rejeita_enunciado_curto(self) -> None:
        with self.assertRaises(ValueError):
            Pergunta(id="x", enunciado="Oi", alternativas=["A", "B"], correta=0)

    def test_rejeita_poucas_alternativas(self) -> None:
        with self.assertRaises(ValueError):
            Pergunta(id="x", enunciado="Pergunta válida?", alternativas=["A"], correta=0)

    def test_rejeita_indice_da_correta_invalido(self) -> None:
        with self.assertRaises(ValueError):
            Pergunta(
                id="x",
                enunciado="Pergunta válida?",
                alternativas=["A", "B"],
                correta=2,
            )

    def test_rejeita_dificuldade_invalida(self) -> None:
        with self.assertRaises(ValueError):
            criar_pergunta(dificuldade="impossivel")

    def test_pontuacao_por_dificuldade(self) -> None:
        self.assertEqual(criar_pergunta("facil").pontos(0), 10)
        self.assertEqual(criar_pergunta("medio").pontos(0), 20)
        self.assertEqual(criar_pergunta("dificil").pontos(0), 30)

    def test_pontuacao_de_resposta_errada_e_zero(self) -> None:
        self.assertEqual(criar_pergunta().pontos(1), 0)

    def test_bonus_de_tempo_limitado_a_cinco(self) -> None:
        pergunta = criar_pergunta("facil")
        self.assertEqual(pergunta.pontos(0, tempo_restante=3), 13)
        self.assertEqual(pergunta.pontos(0, tempo_restante=99), 15)

    def test_para_publico_nao_expoe_a_correta(self) -> None:
        dados = criar_pergunta().para_publico()
        self.assertNotIn("correta", dados)
        self.assertIn("alternativas", dados)

    def test_serializacao_ida_e_volta(self) -> None:
        original = criar_pergunta("dificil", correta=2)
        copia = Pergunta.de_dict(original.para_dict())
        self.assertEqual(copia.para_dict(), original.para_dict())


class TestJogador(unittest.TestCase):
    def test_rejeita_nome_curto(self) -> None:
        with self.assertRaises(ValueError):
            Jogador(nome="A")

    def test_aproveitamento(self) -> None:
        jogador = Jogador(nome="Ana")
        jogador.registrar_resposta(correta=True, pontos=10)
        jogador.registrar_resposta(correta=False, pontos=0)
        jogador.registrar_resposta(correta=True, pontos=20)
        self.assertEqual(jogador.acertos, 2)
        self.assertEqual(jogador.respondidas, 3)
        self.assertEqual(jogador.pontuacao, 30)
        self.assertEqual(jogador.aproveitamento, 66.7)

    def test_aproveitamento_sem_respostas(self) -> None:
        self.assertEqual(Jogador(nome="Bia").aproveitamento, 0.0)


class TestPartida(unittest.TestCase):
    def test_fluxo_completo(self) -> None:
        jogador = Jogador(nome="Carlos")
        partida = Partida(jogador=jogador, perguntas=[criar_pergunta()]).iniciar()

        self.assertEqual(partida.status, "em_andamento")
        self.assertIsNotNone(partida.pergunta_atual())

        resposta = partida.responder(0, tempo_restante=5)

        self.assertTrue(resposta.correta)
        self.assertEqual(resposta.pontos, 15)
        self.assertEqual(partida.status, "finalizada")
        self.assertEqual(jogador.pontuacao, 15)
        self.assertIsNone(partida.pergunta_atual())

    def test_resposta_errada_nao_pontua(self) -> None:
        jogador = Jogador(nome="Dora")
        partida = Partida(jogador=jogador, perguntas=[criar_pergunta()]).iniciar()
        resposta = partida.responder(2)
        self.assertFalse(resposta.correta)
        self.assertEqual(resposta.pontos, 0)
        self.assertEqual(jogador.pontuacao, 0)

    def test_tempo_esgotado_conta_como_erro(self) -> None:
        jogador = Jogador(nome="Edu")
        partida = Partida(jogador=jogador, perguntas=[criar_pergunta()]).iniciar()
        resposta = partida.responder(-1, tempo_restante=0)
        self.assertFalse(resposta.correta)
        self.assertEqual(resposta.pontos, 0)

    def test_rejeita_alternativa_invalida(self) -> None:
        partida = Partida(
            jogador=Jogador(nome="Fabi"),
            perguntas=[criar_pergunta()],
        ).iniciar()
        with self.assertRaises(ValueError):
            partida.responder(9)

    def test_nao_responde_depois_de_finalizada(self) -> None:
        partida = Partida(
            jogador=Jogador(nome="Gil"),
            perguntas=[criar_pergunta()],
        ).iniciar()
        partida.responder(0)
        with self.assertRaises(ValueError):
            partida.responder(0)

    def test_partida_exige_perguntas(self) -> None:
        with self.assertRaises(ValueError):
            Partida(jogador=Jogador(nome="Hugo"), perguntas=[])

    def test_progresso(self) -> None:
        partida = Partida(
            jogador=Jogador(nome="Ivo"),
            perguntas=[criar_pergunta(), criar_pergunta()],
        ).iniciar()
        self.assertEqual(partida.progresso, "0/2")
        partida.responder(0)
        self.assertEqual(partida.progresso, "1/2")


class BaseComRepositorio(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="quiz-core-"))
        shutil.copy(RAIZ / "data" / "perguntas.json", self.tmp / "perguntas.json")
        self.repo = RepositorioJSON(self.tmp)
        self.service = QuizService(self.repo)

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)


class TestRepositorio(BaseComRepositorio):
    def test_carrega_perguntas_do_json(self) -> None:
        self.assertGreaterEqual(len(self.repo.carregar_perguntas()), 1)

    def test_adicionar_e_rejeitar_id_duplicado(self) -> None:
        pergunta = criar_pergunta()
        self.repo.adicionar_pergunta(pergunta)
        with self.assertRaises(ValueError):
            self.repo.adicionar_pergunta(pergunta)

    def test_ranking_ordenado_por_pontuacao(self) -> None:
        menor = Jogador(nome="Menor")
        menor.pontuacao = 10
        maior = Jogador(nome="Maior")
        maior.pontuacao = 90
        self.repo.registrar_no_ranking(menor)
        ranking = self.repo.registrar_no_ranking(maior)
        self.assertEqual(ranking[0]["nome"], "Maior")
        self.assertEqual(ranking[1]["nome"], "Menor")


class TestServico(BaseComRepositorio):
    def test_listar_perguntas_publicas(self) -> None:
        perguntas = self.service.listar_perguntas()
        self.assertGreaterEqual(len(perguntas), 1)
        self.assertTrue(all("correta" not in item for item in perguntas))

    def test_filtrar_por_categoria(self) -> None:
        perguntas = self.service.listar_perguntas(categoria="Python")
        self.assertGreaterEqual(len(perguntas), 1)
        self.assertTrue(all(item["categoria"] == "Python" for item in perguntas))

    def test_iniciar_partida_limita_quantidade(self) -> None:
        partida = self.service.iniciar_partida(nome="Joana", quantidade=3)
        self.assertEqual(partida.total_perguntas, 3)
        self.assertEqual(partida.status, "em_andamento")

    def test_categoria_inexistente_nao_inicia_partida(self) -> None:
        with self.assertRaises(ValueError):
            self.service.iniciar_partida(nome="Léo", categoria="Astronomia")

    def test_partida_finalizada_entra_no_ranking(self) -> None:
        partida = self.service.iniciar_partida(nome="Marina", quantidade=1)
        self.service.responder(partida.id, alternativa=0)
        ranking = self.service.ranking(limite=10)
        self.assertEqual(ranking[0]["nome"], "Marina")

    def test_partida_inexistente(self) -> None:
        with self.assertRaises(KeyError):
            self.service.obter_partida("nao-existe")


if __name__ == "__main__":
    unittest.main()
