"""Quiz Arena Desktop — aplicativo único em Tkinter para Windows.

Uso (a partir da raiz do projeto):
    python desktop/app.py

O app funciona offline: usa diretamente o núcleo em `core/`, sem precisar do
backend Flask nem do navegador. A tela inicial é um menu de cards com:

- Quiz relâmpago (perguntas de múltipla escolha contra o tempo)
- Caça ao Bug (trechos de código com erro para corrigir)
- Ranking (melhores jogadores salvos em JSON)

Os outros componentes do projeto (web, backend e arcade Pygame) continuam
funcionando normalmente; este arquivo é independente.
"""

from __future__ import annotations

import math
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any, Callable

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from core.models import CATEGORIAS_PADRAO, DIFICULDADES
from core.services import QuizService

COR_FUNDO = "#0f172a"
COR_PAINEL = "#1e293b"
COR_PAINEL_ESCURO = "#0b1220"
COR_TEXTO = "#f1f5f9"
COR_TEXTO_FRACO = "#cbd5e1"
COR_DESTAQUE = "#38bdf8"
COR_SUCESSO = "#22c55e"
COR_ERRO = "#f87171"
COR_ALERTA = "#fbbf24"
COR_CARD_QUIZ = "#38bdf8"
COR_CARD_BUG = "#34d399"
COR_CARD_RANKING = "#fbbf24"

LETRAS = "ABCDEFGH"
QUANTIDADES = ("5", "10", "15", "20", "Todas")
DIFICULDADES_ROTULO = {
    "facil": "Fácil",
    "medio": "Médio",
    "dificil": "Difícil",
}


class AplicacaoArena(tk.Tk):
    """Janela principal com o menu de cards e os modos de jogo."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Quiz Arena · Desktop")
        self.geometry("1080x740")
        self.minsize(940, 660)
        self.configure(bg=COR_FUNDO)

        self.service = QuizService()
        self.partida = None
        self._timer_id: str | None = None
        self._pergunta_atual = None

        self.desafios: list[dict[str, Any]] = []
        self.indice_desafio = 0
        self.pontos_desafio = 0
        self.acertos_desafio = 0
        self.desafio_atual: dict[str, Any] | None = None

        self._montar_estilo()

        self.container = tk.Frame(self, bg=COR_FUNDO)
        self.container.pack(fill="both", expand=True)

        self.mostrar_home()

    # ------------------------------------------------------------------ estilo
    def _montar_estilo(self) -> None:
        estilo = ttk.Style(self)
        estilo.theme_use("clam")

        estilo.configure(".", background=COR_FUNDO, foreground=COR_TEXTO)
        estilo.configure("TFrame", background=COR_FUNDO)
        estilo.configure(
            "TLabel",
            background=COR_FUNDO,
            foreground=COR_TEXTO,
            font=("Segoe UI", 11),
        )
        estilo.configure(
            "TButton",
            background="#334155",
            foreground=COR_TEXTO,
            borderwidth=0,
            padding=(14, 10),
            font=("Segoe UI", 11, "bold"),
        )
        estilo.map("TButton", background=[("active", "#475569")])
        estilo.configure(
            "Destaque.TButton",
            background=COR_DESTAQUE,
            foreground="#082f49",
        )
        estilo.map("Destaque.TButton", background=[("active", "#7dd3fc")])
        estilo.configure(
            "Sucesso.TButton",
            background=COR_SUCESSO,
            foreground="#052e16",
        )
        estilo.map("Sucesso.TButton", background=[("active", "#4ade80")])
        estilo.configure(
            "TEntry",
            fieldbackground=COR_PAINEL_ESCURO,
            foreground=COR_TEXTO,
            insertcolor=COR_TEXTO,
            borderwidth=0,
            padding=8,
            font=("Segoe UI", 11),
        )
        estilo.configure(
            "TCombobox",
            fieldbackground=COR_PAINEL_ESCURO,
            background="#334155",
            foreground=COR_TEXTO,
            arrowcolor=COR_TEXTO,
            borderwidth=0,
            padding=6,
            font=("Segoe UI", 11),
        )
        estilo.configure(
            "TSpinbox",
            fieldbackground=COR_PAINEL_ESCURO,
            foreground=COR_TEXTO,
            arrowcolor=COR_TEXTO,
            borderwidth=0,
            padding=6,
            font=("Segoe UI", 11),
        )
        estilo.configure(
            "Treeview",
            background=COR_PAINEL_ESCURO,
            fieldbackground=COR_PAINEL_ESCURO,
            foreground=COR_TEXTO,
            rowheight=32,
            borderwidth=0,
            font=("Segoe UI", 11),
        )
        estilo.configure(
            "Treeview.Heading",
            background="#334155",
            foreground=COR_TEXTO,
            font=("Segoe UI", 10, "bold"),
            padding=6,
        )
        estilo.map("Treeview", background=[("selected", "#0369a1")])

    # ------------------------------------------------------------- utilidades
    def _limpar_container(self) -> None:
        self._parar_timer()
        for widget in self.container.winfo_children():
            widget.destroy()

    def _parar_timer(self) -> None:
        if self._timer_id is not None:
            try:
                self.after_cancel(self._timer_id)
            except tk.TclError:
                pass
            self._timer_id = None

    def _ligar_clique(self, widget: tk.Misc, comando: Callable[[], None]) -> None:
        widget.bind("<Button-1>", lambda _evento: comando())
        try:
            widget.configure(cursor="hand2")
        except tk.TclError:
            pass

    def _cabecalho(self, parent: tk.Misc, subtitulo: str, voltar=None) -> None:
        barra = tk.Frame(parent, bg=COR_FUNDO)
        barra.pack(fill="x", pady=(0, 18))

        esquerda = tk.Frame(barra, bg=COR_FUNDO)
        esquerda.pack(side="left", anchor="w")

        tk.Label(
            esquerda,
            text="QUIZ ARENA",
            bg=COR_FUNDO,
            fg=COR_DESTAQUE,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")
        tk.Label(
            esquerda,
            text=subtitulo,
            bg=COR_FUNDO,
            fg=COR_TEXTO,
            font=("Segoe UI", 20, "bold"),
        ).pack(anchor="w")

        if voltar is not None:
            ttk.Button(barra, text="← Menu", command=voltar).pack(side="right")

    # ------------------------------------------------------------------- home
    def mostrar_home(self) -> None:
        self._limpar_container()
        self.partida = None
        self._pergunta_atual = None

        wrapper = tk.Frame(self.container, bg=COR_FUNDO)
        wrapper.pack(fill="both", expand=True, padx=30, pady=26)

        self._cabecalho(wrapper, "Mostre o que você aprendeu")

        tk.Label(
            wrapper,
            text="Escolha um modo",
            bg=COR_FUNDO,
            fg=COR_DESTAQUE,
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="center", pady=(6, 2))
        tk.Label(
            wrapper,
            text="Duas formas de treinar o que você aprendeu.",
            bg=COR_FUNDO,
            fg=COR_TEXTO,
            font=("Segoe UI", 24, "bold"),
        ).pack(anchor="center")
        tk.Label(
            wrapper,
            text=(
                "Jogue o quiz tradicional ou teste seu olhar de programador no "
                "Caça ao Bug. O ranking guarda o melhor resultado de cada jogador."
            ),
            bg=COR_FUNDO,
            fg=COR_TEXTO_FRACO,
            font=("Segoe UI", 12),
            wraplength=820,
            justify="center",
        ).pack(anchor="center", pady=(6, 24))

        cards = tk.Frame(wrapper, bg=COR_FUNDO)
        cards.pack(fill="both", expand=True)

        self._criar_card(
            cards,
            0,
            "🎯",
            "Quiz relâmpago",
            "Perguntas de múltipla escolha contra o tempo. Quanto mais rápido, "
            "maior o bônus.",
            "Python · POO · Web · React · Git",
            COR_CARD_QUIZ,
            "Jogar quiz",
            self.mostrar_config_quiz,
        )
        self._criar_card(
            cards,
            1,
            "🐞",
            "Caça ao Bug",
            "Um trecho de código com erro aparece na tela. Descubra qual "
            "correção resolve o problema.",
            "Python · React · Flask · Git",
            COR_CARD_BUG,
            "Caçar bugs",
            self.mostrar_cacabug,
        )
        self._criar_card(
            cards,
            2,
            "🏆",
            "Ranking",
            "Veja a melhor partida de cada jogador e quantas vezes já entraram "
            "na arena.",
            "Pontuação · Aproveitamento",
            COR_CARD_RANKING,
            "Ver ranking",
            self.mostrar_ranking,
        )

        tk.Label(
            wrapper,
            text=(
                "Modo offline · usa o mesmo core/ do backend Flask e do modo "
                "arcade. Nenhum servidor é necessário."
            ),
            bg=COR_FUNDO,
            fg="#94a3b8",
            font=("Segoe UI", 10),
        ).pack(anchor="center", pady=(18, 0))

    def _criar_card(
        self,
        parent: tk.Misc,
        coluna: int,
        icone: str,
        titulo: str,
        descricao: str,
        topicos: str,
        cor: str,
        rotulo_botao: str,
        comando: Callable[[], None],
    ) -> None:
        parent.columnconfigure(coluna, weight=1, uniform="card")

        card = tk.Frame(
            parent,
            bg=COR_PAINEL,
            highlightbackground=cor,
            highlightthickness=2,
            padx=18,
            pady=18,
        )
        card.grid(row=0, column=coluna, sticky="nsew", padx=8, pady=8)
        card.rowconfigure(2, weight=1)

        icone_lbl = tk.Label(
            card,
            text=icone,
            bg=COR_PAINEL,
            fg=COR_TEXTO,
            font=("Segoe UI Emoji", 30),
        )
        icone_lbl.grid(row=0, column=0, sticky="w")

        titulo_lbl = tk.Label(
            card,
            text=titulo.upper(),
            bg=COR_PAINEL,
            fg=cor,
            font=("Segoe UI", 12, "bold"),
        )
        titulo_lbl.grid(row=1, column=0, sticky="w", pady=(8, 4))

        descricao_lbl = tk.Label(
            card,
            text=descricao,
            bg=COR_PAINEL,
            fg=COR_TEXTO_FRACO,
            font=("Segoe UI", 12),
            wraplength=250,
            justify="left",
        )
        descricao_lbl.grid(row=2, column=0, sticky="new")

        topicos_lbl = tk.Label(
            card,
            text=topicos.upper(),
            bg=COR_PAINEL,
            fg="#94a3b8",
            font=("Segoe UI", 10, "bold"),
        )
        topicos_lbl.grid(row=3, column=0, sticky="w", pady=(10, 12))

        botao = ttk.Button(
            card,
            text=f"{rotulo_botao} →",
            style="Destaque.TButton",
            command=comando,
        )
        botao.grid(row=4, column=0, sticky="ew")

        for widget in (card, icone_lbl, titulo_lbl, descricao_lbl, topicos_lbl):
            self._ligar_clique(widget, comando)

    # -------------------------------------------------------------- quiz setup
    def mostrar_config_quiz(self) -> None:
        self._limpar_container()

        wrapper = tk.Frame(self.container, bg=COR_FUNDO)
        wrapper.pack(fill="both", expand=True, padx=30, pady=26)

        self._cabecalho(wrapper, "Quiz relâmpago", voltar=self.mostrar_home)

        tk.Label(
            wrapper,
            text="Entre na arena e responda antes do tempo acabar.",
            bg=COR_FUNDO,
            fg=COR_TEXTO,
            font=("Segoe UI", 22, "bold"),
        ).pack(anchor="w")
        tk.Label(
            wrapper,
            text=(
                "Perguntas de Python, POO, Web, React, Backend, Git e Games. "
                "Cada acerto vale pontos e o tempo restante dá bônus."
            ),
            bg=COR_FUNDO,
            fg=COR_TEXTO_FRACO,
            font=("Segoe UI", 12),
            wraplength=860,
            justify="left",
        ).pack(anchor="w", pady=(6, 20))

        formulario = tk.Frame(
            wrapper,
            bg=COR_PAINEL,
            highlightbackground="#334155",
            highlightthickness=1,
            padx=22,
            pady=20,
        )
        formulario.pack(fill="x")

        tk.Label(
            formulario,
            text="Seu nome",
            bg=COR_PAINEL,
            fg=COR_TEXTO,
            font=("Segoe UI", 11, "bold"),
        ).grid(row=0, column=0, columnspan=4, sticky="w")
        self.entrada_nome = ttk.Entry(formulario, width=40)
        self.entrada_nome.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(4, 16))
        self.entrada_nome.insert(0, "Jogador 1")
        formulario.columnconfigure(0, weight=1)

        categorias = self._categorias_disponiveis()
        self.combo_categoria = self._campo_combo(
            formulario, 0, "Categoria", ["Todas"] + categorias, "Todas"
        )
        self.combo_quantidade = self._campo_combo(
            formulario, 1, "Quantidade", list(QUANTIDADES), "10"
        )
        self.combo_dificuldade = self._campo_combo(
            formulario,
            2,
            "Dificuldade",
            ["Todas"] + list(DIFICULDADES_ROTULO.values()),
            "Todas",
        )

        acoes = tk.Frame(wrapper, bg=COR_FUNDO)
        acoes.pack(fill="x", pady=(20, 0))
        ttk.Button(
            acoes,
            text="Começar partida",
            style="Destaque.TButton",
            command=self._iniciar_partida,
        ).pack(side="left")
        ttk.Button(acoes, text="Voltar ao menu", command=self.mostrar_home).pack(
            side="left", padx=10
        )

    def _campo_combo(
        self,
        parent: tk.Misc,
        coluna: int,
        rotulo: str,
        valores: list[str],
        inicial: str,
    ) -> ttk.Combobox:
        tk.Label(
            parent,
            text=rotulo,
            bg=COR_PAINEL,
            fg=COR_TEXTO,
            font=("Segoe UI", 11, "bold"),
        ).grid(row=2, column=coluna, sticky="w", padx=(0, 14))
        combo = ttk.Combobox(parent, values=valores, state="readonly", width=18)
        combo.grid(row=3, column=coluna, sticky="w", padx=(0, 14))
        combo.set(inicial)
        return combo

    def _categorias_disponiveis(self) -> list[str]:
        categorias = set(CATEGORIAS_PADRAO)
        try:
            categorias.update(
                pergunta["categoria"] for pergunta in self.service.listar_perguntas()
            )
        except Exception:  # noqa: BLE001 - categorias são auxiliares
            pass
        return sorted(categorias)

    def _iniciar_partida(self) -> None:
        nome = self.entrada_nome.get().strip()
        if len(nome) < 2:
            messagebox.showwarning("Nome inválido", "Informe pelo menos 2 caracteres.")
            return

        categoria = self.combo_categoria.get()
        categoria = None if categoria in ("", "Todas") else categoria

        quantidade = self.combo_quantidade.get()
        quantidade = None if quantidade == "Todas" else int(quantidade)

        rotulo_dificuldade = self.combo_dificuldade.get()
        dificuldade = None
        for chave, rotulo in DIFICULDADES_ROTULO.items():
            if rotulo == rotulo_dificuldade:
                dificuldade = chave
                break

        try:
            self.partida = self.service.iniciar_partida(
                nome=nome,
                quantidade=quantidade,
                categoria=categoria,
                dificuldade=dificuldade,
            )
        except ValueError as erro:
            messagebox.showerror("Não foi possível iniciar", str(erro))
            return

        self.mostrar_quiz()

    # ------------------------------------------------------------------- quiz
    def mostrar_quiz(self) -> None:
        self._limpar_container()

        if self.partida is None:
            self.mostrar_home()
            return

        wrapper = tk.Frame(self.container, bg=COR_FUNDO)
        wrapper.pack(fill="both", expand=True, padx=30, pady=26)

        topo = tk.Frame(wrapper, bg=COR_FUNDO)
        topo.pack(fill="x")
        self.lbl_progresso_quiz = tk.Label(
            topo,
            text="",
            bg=COR_FUNDO,
            fg=COR_DESTAQUE,
            font=("Segoe UI", 11, "bold"),
        )
        self.lbl_progresso_quiz.pack(side="left")
        self.lbl_tempo_quiz = tk.Label(
            topo,
            text="",
            bg=COR_FUNDO,
            fg=COR_DESTAQUE,
            font=("Segoe UI", 15, "bold"),
        )
        self.lbl_tempo_quiz.pack(side="right")
        ttk.Button(topo, text="Sair", command=self.mostrar_home).pack(
            side="right", padx=12
        )

        painel = tk.Frame(
            wrapper,
            bg=COR_PAINEL,
            highlightbackground="#334155",
            highlightthickness=1,
            padx=24,
            pady=22,
        )
        painel.pack(fill="both", expand=True, pady=(16, 0))

        self.lbl_pergunta_quiz = tk.Label(
            painel,
            text="",
            bg=COR_PAINEL,
            fg=COR_TEXTO,
            font=("Segoe UI", 19, "bold"),
            wraplength=940,
            justify="left",
            anchor="w",
        )
        self.lbl_pergunta_quiz.pack(fill="x", anchor="w", pady=(0, 16))

        self.frame_alternativas = tk.Frame(painel, bg=COR_PAINEL)
        self.frame_alternativas.pack(fill="x", anchor="w")
        self.alternativa_var = tk.StringVar(value="")

        self.lbl_feedback_quiz = tk.Label(
            painel,
            text="",
            bg=COR_PAINEL,
            fg=COR_TEXTO,
            font=("Segoe UI", 12, "bold"),
            wraplength=940,
            justify="left",
            anchor="w",
        )
        self.lbl_feedback_quiz.pack(fill="x", anchor="w", pady=(16, 10))

        self.lbl_placar_quiz = tk.Label(
            painel,
            text="",
            bg=COR_PAINEL,
            fg=COR_TEXTO_FRACO,
            font=("Segoe UI", 11),
            anchor="w",
        )
        self.lbl_placar_quiz.pack(fill="x", anchor="w", pady=(0, 12))

        self.btn_acao_quiz = ttk.Button(
            painel,
            text="Responder",
            style="Destaque.TButton",
            command=self._responder_quiz,
        )
        self.btn_acao_quiz.pack(anchor="w")

        self._atualizar_quiz()

    def _atualizar_quiz(self) -> None:
        self._parar_timer()

        if self.partida is None:
            self.mostrar_home()
            return

        pergunta = self.partida.pergunta_atual()
        if pergunta is None:
            self.mostrar_resultado()
            return

        self._pergunta_atual = pergunta
        self.lbl_progresso_quiz.configure(
            text=(
                f"Pergunta {self.partida.indice_atual + 1} de "
                f"{self.partida.total_perguntas} · {pergunta.categoria} · "
                f"{DIFICULDADES_ROTULO.get(pergunta.dificuldade, pergunta.dificuldade)}"
            )
        )
        self.lbl_pergunta_quiz.configure(text=pergunta.enunciado)

        self.alternativa_var.set("")
        for widget in self.frame_alternativas.winfo_children():
            widget.destroy()

        for indice, alternativa in enumerate(pergunta.alternativas):
            letra = LETRAS[indice] if indice < len(LETRAS) else str(indice + 1)
            tk.Radiobutton(
                self.frame_alternativas,
                text=f"{letra}) {alternativa}",
                variable=self.alternativa_var,
                value=str(indice),
                bg=COR_PAINEL,
                fg=COR_TEXTO,
                activebackground=COR_PAINEL,
                activeforeground=COR_DESTAQUE,
                selectcolor=COR_PAINEL_ESCURO,
                font=("Segoe UI", 12),
                anchor="w",
                justify="left",
                wraplength=920,
                padx=6,
                pady=4,
                borderwidth=0,
                highlightthickness=0,
                cursor="hand2",
            ).pack(fill="x", anchor="w")

        self.lbl_feedback_quiz.configure(text="")
        self.lbl_placar_quiz.configure(
            text=(
                f"Placar: {self.partida.jogador.pontuacao} pontos · "
                f"{self.partida.jogador.acertos} acerto(s)"
            )
        )
        self.btn_acao_quiz.configure(
            text="Responder", style="Destaque.TButton", command=self._responder_quiz
        )
        self._tick_quiz()

    def _tick_quiz(self) -> None:
        if self.partida is None or self.partida.status != "em_andamento":
            return

        restante = self.partida.tempo_restante_servidor()
        segundos = max(0, math.ceil(restante))
        cor = COR_ERRO if segundos <= 5 else COR_DESTAQUE
        self.lbl_tempo_quiz.configure(text=f"⏱ {segundos}s", fg=cor)

        if restante <= 0:
            self._responder_quiz(alternativa=-1)
            return

        self._timer_id = self.after(300, self._tick_quiz)

    def _responder_quiz(self, alternativa: int | None = None) -> None:
        if self.partida is None or self.partida.status != "em_andamento":
            return

        if alternativa is None:
            escolha = self.alternativa_var.get()
            if escolha == "":
                messagebox.showinfo("Escolha uma alternativa", "Marque A, B, C ou D.")
                return
            alternativa = int(escolha)

        self._parar_timer()

        pergunta = self.partida.pergunta_atual()
        try:
            _, pergunta, resposta = self.service.responder(
                partida_id=self.partida.id,
                alternativa=alternativa,
                pergunta_id=pergunta.id if pergunta else None,
            )
        except (KeyError, ValueError) as erro:
            messagebox.showerror("Erro ao responder", str(erro))
            return

        correta = pergunta.alternativas[pergunta.correta]
        if resposta.correta:
            texto = f"✅ Correto! +{resposta.pontos} pontos"
            cor = COR_SUCESSO
        elif alternativa == -1:
            texto = f"⏰ Tempo esgotado! Resposta correta: {correta}"
            cor = COR_ERRO
        else:
            texto = f"❌ Errado! Resposta correta: {correta}"
            cor = COR_ERRO

        if pergunta.explicacao:
            texto = f"{texto}\n💡 {pergunta.explicacao}"

        self.lbl_feedback_quiz.configure(text=texto, fg=cor)
        self.lbl_placar_quiz.configure(
            text=(
                f"Placar: {self.partida.jogador.pontuacao} pontos · "
                f"{self.partida.jogador.acertos} acerto(s)"
            )
        )
        self.lbl_tempo_quiz.configure(text="")

        if self.partida.status == "finalizada":
            self.btn_acao_quiz.configure(
                text="Ver resultado",
                style="Sucesso.TButton",
                command=self.mostrar_resultado,
            )
        else:
            self.btn_acao_quiz.configure(
                text="Próxima pergunta →",
                style="Destaque.TButton",
                command=self._atualizar_quiz,
            )

    def mostrar_resultado(self) -> None:
        self._parar_timer()

        if self.partida is None:
            self.mostrar_home()
            return

        self._limpar_container()
        jogador = self.partida.jogador

        wrapper = tk.Frame(self.container, bg=COR_FUNDO)
        wrapper.pack(fill="both", expand=True, padx=30, pady=26)

        self._cabecalho(wrapper, "Resultado da partida", voltar=self.mostrar_home)

        tk.Label(
            wrapper,
            text=f"🏁 Fim de jogo, {jogador.nome}!",
            bg=COR_FUNDO,
            fg=COR_TEXTO,
            font=("Segoe UI", 24, "bold"),
        ).pack(anchor="w")

        resumo = tk.Frame(wrapper, bg=COR_FUNDO)
        resumo.pack(fill="x", pady=(16, 18))
        for rotulo, valor, cor in (
            ("Pontos", str(jogador.pontuacao), COR_DESTAQUE),
            ("Acertos", f"{jogador.acertos}/{jogador.respondidas}", COR_SUCESSO),
            ("Aproveitamento", f"{jogador.aproveitamento}%", COR_ALERTA),
        ):
            bloco = tk.Frame(
                resumo,
                bg=COR_PAINEL,
                highlightbackground="#334155",
                highlightthickness=1,
                padx=18,
                pady=14,
            )
            bloco.pack(side="left", expand=True, fill="x", padx=6)
            tk.Label(
                bloco,
                text=rotulo.upper(),
                bg=COR_PAINEL,
                fg=COR_TEXTO_FRACO,
                font=("Segoe UI", 10, "bold"),
            ).pack(anchor="w")
            tk.Label(
                bloco,
                text=valor,
                bg=COR_PAINEL,
                fg=cor,
                font=("Segoe UI", 24, "bold"),
            ).pack(anchor="w")

        tk.Label(
            wrapper,
            text="Revisão das respostas",
            bg=COR_FUNDO,
            fg=COR_TEXTO,
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        area = tk.Frame(wrapper, bg=COR_PAINEL_ESCURO)
        area.pack(fill="both", expand=True)
        texto = tk.Text(
            area,
            bg=COR_PAINEL_ESCURO,
            fg=COR_TEXTO,
            insertbackground=COR_TEXTO,
            font=("Segoe UI", 12),
            wrap="word",
            padx=14,
            pady=12,
            borderwidth=0,
            highlightthickness=0,
        )
        barra = ttk.Scrollbar(area, orient="vertical", command=texto.yview)
        texto.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        texto.pack(side="left", fill="both", expand=True)

        for numero, item in enumerate(self.partida.revisao(), start=1):
            marca = "✅" if item["acertou"] else "❌"
            texto.insert(
                "end",
                f"{marca} {numero}. {item['enunciado']}\n"
                f"   Sua resposta: {item['escolhida'] or '—'}\n"
                f"   Correta: {item['correta']}  ·  +{item['pontos']} pontos\n",
            )
            if item["explicacao"]:
                texto.insert("end", f"   💡 {item['explicacao']}\n")
            texto.insert("end", "\n")
        texto.configure(state="disabled")

        acoes = tk.Frame(wrapper, bg=COR_FUNDO)
        acoes.pack(fill="x", pady=(18, 0))
        ttk.Button(
            acoes,
            text="Jogar de novo",
            style="Destaque.TButton",
            command=self.mostrar_config_quiz,
        ).pack(side="left")
        ttk.Button(acoes, text="Ver ranking", command=self.mostrar_ranking).pack(
            side="left", padx=10
        )
        ttk.Button(acoes, text="Voltar ao menu", command=self.mostrar_home).pack(
            side="left"
        )

    # -------------------------------------------------------------- caça ao bug
    def mostrar_cacabug(self) -> None:
        self._limpar_container()

        try:
            self.desafios = self.service.listar_desafios(publico=True)
        except Exception as erro:  # noqa: BLE001 - não quebrar a janela
            messagebox.showerror("Erro ao carregar desafios", str(erro))
            self.desafios = []

        self.indice_desafio = 0
        self.pontos_desafio = 0
        self.acertos_desafio = 0

        if not self.desafios:
            wrapper = tk.Frame(self.container, bg=COR_FUNDO)
            wrapper.pack(fill="both", expand=True, padx=30, pady=26)
            self._cabecalho(wrapper, "Caça ao Bug", voltar=self.mostrar_home)
            tk.Label(
                wrapper,
                text=(
                    "Nenhum desafio cadastrado em data/desafios.json.\n"
                    "Adicione desafios para jogar este modo."
                ),
                bg=COR_FUNDO,
                fg=COR_TEXTO_FRACO,
                font=("Segoe UI", 12),
                justify="left",
            ).pack(anchor="w", pady=20)
            ttk.Button(wrapper, text="Voltar ao menu", command=self.mostrar_home).pack(
                anchor="w"
            )
            return

        wrapper = tk.Frame(self.container, bg=COR_FUNDO)
        wrapper.pack(fill="both", expand=True, padx=30, pady=26)

        topo = tk.Frame(wrapper, bg=COR_FUNDO)
        topo.pack(fill="x")
        self.lbl_progresso_bug = tk.Label(
            topo,
            text="",
            bg=COR_FUNDO,
            fg=COR_CARD_BUG,
            font=("Segoe UI", 11, "bold"),
        )
        self.lbl_progresso_bug.pack(side="left")
        self.lbl_placar_bug = tk.Label(
            topo,
            text="",
            bg=COR_FUNDO,
            fg=COR_CARD_BUG,
            font=("Segoe UI", 14, "bold"),
        )
        self.lbl_placar_bug.pack(side="right")
        ttk.Button(topo, text="Sair", command=self.mostrar_home).pack(
            side="right", padx=12
        )

        painel = tk.Frame(
            wrapper,
            bg=COR_PAINEL,
            highlightbackground="#334155",
            highlightthickness=1,
            padx=24,
            pady=20,
        )
        painel.pack(fill="both", expand=True, pady=(16, 0))

        self.lbl_titulo_bug = tk.Label(
            painel,
            text="",
            bg=COR_PAINEL,
            fg=COR_TEXTO,
            font=("Segoe UI", 18, "bold"),
            anchor="w",
            justify="left",
        )
        self.lbl_titulo_bug.pack(fill="x", anchor="w")

        self.lbl_meta_bug = tk.Label(
            painel,
            text="",
            bg=COR_PAINEL,
            fg=COR_TEXTO_FRACO,
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        )
        self.lbl_meta_bug.pack(fill="x", anchor="w", pady=(2, 10))

        self.txt_codigo_bug = tk.Text(
            painel,
            bg=COR_PAINEL_ESCURO,
            fg="#a7f3d0",
            insertbackground="#a7f3d0",
            font=("Consolas", 12),
            wrap="word",
            height=7,
            padx=12,
            pady=10,
            borderwidth=0,
            highlightthickness=0,
        )
        self.txt_codigo_bug.pack(fill="x")

        self.lbl_descricao_bug = tk.Label(
            painel,
            text="",
            bg=COR_PAINEL,
            fg=COR_TEXTO,
            font=("Segoe UI", 12),
            wraplength=940,
            justify="left",
            anchor="w",
        )
        self.lbl_descricao_bug.pack(fill="x", anchor="w", pady=(14, 12))

        self.frame_alternativas_bug = tk.Frame(painel, bg=COR_PAINEL)
        self.frame_alternativas_bug.pack(fill="x", anchor="w")
        self.alternativa_bug_var = tk.StringVar(value="")

        self.lbl_feedback_bug = tk.Label(
            painel,
            text="",
            bg=COR_PAINEL,
            fg=COR_TEXTO,
            font=("Segoe UI", 12, "bold"),
            wraplength=940,
            justify="left",
            anchor="w",
        )
        self.lbl_feedback_bug.pack(fill="x", anchor="w", pady=(14, 10))

        self.btn_acao_bug = ttk.Button(
            painel,
            text="Responder",
            style="Destaque.TButton",
            command=self._responder_bug,
        )
        self.btn_acao_bug.pack(anchor="w")

        self._atualizar_desafio()

    def _atualizar_desafio(self) -> None:
        if self.indice_desafio >= len(self.desafios):
            self._resultado_cacabug()
            return

        desafio = self.desafios[self.indice_desafio]
        self.desafio_atual = desafio

        self.lbl_progresso_bug.configure(
            text=f"CAÇA AO BUG · {self.indice_desafio + 1} DE {len(self.desafios)}"
        )
        self.lbl_placar_bug.configure(
            text=f"{self.pontos_desafio} pts · {self.acertos_desafio} acerto(s)"
        )
        self.lbl_titulo_bug.configure(text=desafio["titulo"])
        self.lbl_meta_bug.configure(
            text=f"{desafio['linguagem']} · {desafio['tema']}"
        )
        self.lbl_descricao_bug.configure(text=desafio["descricao"])

        self.txt_codigo_bug.configure(state="normal")
        self.txt_codigo_bug.delete("1.0", "end")
        self.txt_codigo_bug.insert("1.0", desafio["codigo"])
        linhas = max(3, min(12, desafio["codigo"].count("\n") + 1))
        self.txt_codigo_bug.configure(height=linhas, state="disabled")

        self.alternativa_bug_var.set("")
        for widget in self.frame_alternativas_bug.winfo_children():
            widget.destroy()

        for indice, alternativa in enumerate(desafio["alternativas"]):
            letra = LETRAS[indice] if indice < len(LETRAS) else str(indice + 1)
            tk.Radiobutton(
                self.frame_alternativas_bug,
                text=f"{letra}) {alternativa}",
                variable=self.alternativa_bug_var,
                value=str(indice),
                bg=COR_PAINEL,
                fg=COR_TEXTO,
                activebackground=COR_PAINEL,
                activeforeground=COR_CARD_BUG,
                selectcolor=COR_PAINEL_ESCURO,
                font=("Segoe UI", 12),
                anchor="w",
                justify="left",
                wraplength=920,
                padx=6,
                pady=4,
                borderwidth=0,
                highlightthickness=0,
                cursor="hand2",
            ).pack(fill="x", anchor="w")

        self.lbl_feedback_bug.configure(text="")
        self.btn_acao_bug.configure(
            text="Responder", style="Destaque.TButton", command=self._responder_bug
        )

    def _responder_bug(self) -> None:
        if self.desafio_atual is None:
            return

        escolha = self.alternativa_bug_var.get()
        if escolha == "":
            messagebox.showinfo("Escolha uma alternativa", "Marque A, B, C ou D.")
            return

        try:
            desafio, correta, pontos = self.service.responder_desafio(
                self.desafio_atual["id"], int(escolha)
            )
        except (KeyError, ValueError) as erro:
            messagebox.showerror("Erro ao responder", str(erro))
            return

        if correta:
            self.pontos_desafio += pontos
            self.acertos_desafio += 1
            texto = f"✅ Bug encontrado! +{pontos} pontos"
            cor = COR_SUCESSO
        else:
            texto = (
                "❌ Ainda não. A correção certa era: "
                f"{desafio.alternativas[desafio.correta]}"
            )
            cor = COR_ERRO

        if desafio.explicacao:
            texto = f"{texto}\n💡 {desafio.explicacao}"

        self.lbl_feedback_bug.configure(text=texto, fg=cor)
        self.lbl_placar_bug.configure(
            text=f"{self.pontos_desafio} pts · {self.acertos_desafio} acerto(s)"
        )

        if self.indice_desafio + 1 >= len(self.desafios):
            self.btn_acao_bug.configure(
                text="Ver resultado",
                style="Sucesso.TButton",
                command=self._resultado_cacabug,
            )
        else:
            self.btn_acao_bug.configure(
                text="Próximo desafio →",
                style="Destaque.TButton",
                command=self._proximo_desafio,
            )

    def _proximo_desafio(self) -> None:
        self.indice_desafio += 1
        self._atualizar_desafio()

    def _resultado_cacabug(self) -> None:
        self._limpar_container()

        total = len(self.desafios) or 1
        aproveitamento = round(self.acertos_desafio / total * 100)

        wrapper = tk.Frame(self.container, bg=COR_FUNDO)
        wrapper.pack(fill="both", expand=True, padx=30, pady=26)

        self._cabecalho(wrapper, "Fim dos desafios", voltar=self.mostrar_home)

        tk.Label(
            wrapper,
            text=f"{self.acertos_desafio} de {total} bugs encontrados!",
            bg=COR_FUNDO,
            fg=COR_TEXTO,
            font=("Segoe UI", 24, "bold"),
        ).pack(anchor="w", pady=(4, 18))

        resumo = tk.Frame(wrapper, bg=COR_FUNDO)
        resumo.pack(fill="x")
        for rotulo, valor, cor in (
            ("Pontos", str(self.pontos_desafio), COR_DESTAQUE),
            ("Acertos", f"{self.acertos_desafio}/{total}", COR_SUCESSO),
            ("Aproveitamento", f"{aproveitamento}%", COR_ALERTA),
        ):
            bloco = tk.Frame(
                resumo,
                bg=COR_PAINEL,
                highlightbackground="#334155",
                highlightthickness=1,
                padx=18,
                pady=14,
            )
            bloco.pack(side="left", expand=True, fill="x", padx=6)
            tk.Label(
                bloco,
                text=rotulo.upper(),
                bg=COR_PAINEL,
                fg=COR_TEXTO_FRACO,
                font=("Segoe UI", 10, "bold"),
            ).pack(anchor="w")
            tk.Label(
                bloco,
                text=valor,
                bg=COR_PAINEL,
                fg=cor,
                font=("Segoe UI", 24, "bold"),
            ).pack(anchor="w")

        acoes = tk.Frame(wrapper, bg=COR_FUNDO)
        acoes.pack(fill="x", pady=(22, 0))
        ttk.Button(
            acoes,
            text="Jogar de novo",
            style="Sucesso.TButton",
            command=self.mostrar_cacabug,
        ).pack(side="left")
        ttk.Button(acoes, text="Voltar ao menu", command=self.mostrar_home).pack(
            side="left", padx=10
        )

    # ---------------------------------------------------------------- ranking
    def mostrar_ranking(self) -> None:
        self._limpar_container()

        wrapper = tk.Frame(self.container, bg=COR_FUNDO)
        wrapper.pack(fill="both", expand=True, padx=30, pady=26)

        self._cabecalho(wrapper, "🏆 Ranking", voltar=self.mostrar_home)

        tk.Label(
            wrapper,
            text="Melhores partidas por jogador",
            bg=COR_FUNDO,
            fg=COR_TEXTO_FRACO,
            font=("Segoe UI", 12),
        ).pack(anchor="w", pady=(0, 12))

        area = tk.Frame(wrapper, bg=COR_FUNDO)
        area.pack(fill="both", expand=True)

        colunas = ("posicao", "nome", "pontos", "acertos", "aproveitamento", "partidas")
        tree = ttk.Treeview(area, columns=colunas, show="headings", height=16)
        titulos = {
            "posicao": ("#", 50),
            "nome": ("Jogador", 300),
            "pontos": ("Pontos", 90),
            "acertos": ("Acertos", 90),
            "aproveitamento": ("%", 80),
            "partidas": ("Partidas", 90),
        }
        for coluna, (titulo, largura) in titulos.items():
            tree.heading(coluna, text=titulo)
            tree.column(coluna, width=largura, anchor="center")
        tree.column("nome", anchor="w")

        barra = ttk.Scrollbar(area, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        tree.pack(side="left", fill="both", expand=True)

        def carregar() -> None:
            for item in tree.get_children():
                tree.delete(item)
            try:
                ranking = self.service.ranking(limite=50)
            except Exception as erro:  # noqa: BLE001 - não quebrar a janela
                messagebox.showerror("Erro no ranking", str(erro))
                return
            for posicao, jogador in enumerate(ranking, start=1):
                tree.insert(
                    "",
                    "end",
                    values=(
                        f"{posicao}º",
                        jogador.get("nome", "?"),
                        jogador.get("pontuacao", 0),
                        jogador.get("acertos", 0),
                        f"{jogador.get('aproveitamento', 0)}%",
                        jogador.get("partidas", 1),
                    ),
                )

        carregar()

        acoes = tk.Frame(wrapper, bg=COR_FUNDO)
        acoes.pack(fill="x", pady=(14, 0))
        ttk.Button(acoes, text="Atualizar", command=carregar).pack(side="left")
        ttk.Button(acoes, text="Voltar ao menu", command=self.mostrar_home).pack(
            side="left", padx=10
        )


def main() -> None:
    app = AplicacaoArena()
    app.mainloop()


if __name__ == "__main__":
    main()
