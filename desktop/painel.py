"""Painel desktop do Quiz Arena (Tkinter).

Uso (a partir da raiz do projeto):
    python desktop/painel.py

O apresentador usa este painel para iniciar partidas, acompanhar o tempo,
responder as perguntas e cadastrar novas perguntas. Ele compartilha o mesmo
núcleo (`core/`) usado pelo backend FastAPI.
"""

from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from core.models import CATEGORIAS_PADRAO, DIFICULDADES
from core.services import QuizService

COR_FUNDO = "#0f172a"
COR_PAINEL = "#1e293b"
COR_TEXTO = "#e2e8f0"
COR_TEXTO_FRACO = "#94a3b8"
COR_DESTAQUE = "#38bdf8"
COR_SUCESSO = "#22c55e"
COR_ERRO = "#f87171"

LETRAS = "ABCDEFGH"


class AplicacaoQuiz(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Quiz Arena · Painel do Apresentador")
        self.geometry("1020x700")
        self.minsize(880, 600)
        self.configure(bg=COR_FUNDO)

        self.service = QuizService()
        self.partida = None
        self.tempo_restante = 0
        self.timer_id: str | None = None

        self._montar_estilo()
        self._montar_abas()
        self._atualizar_categorias()
        self._carregar_perguntas()
        self._atualizar_ranking()

    # ------------------------------------------------------------------ UI
    def _montar_estilo(self) -> None:
        estilo = ttk.Style(self)
        estilo.theme_use("clam")

        estilo.configure(".", background=COR_FUNDO, foreground=COR_TEXTO)
        estilo.configure("TFrame", background=COR_FUNDO)
        estilo.configure("Painel.TFrame", background=COR_PAINEL)
        estilo.configure(
            "TLabel",
            background=COR_FUNDO,
            foreground=COR_TEXTO,
            font=("Segoe UI", 10),
        )
        estilo.configure(
            "Painel.TLabel",
            background=COR_PAINEL,
            foreground=COR_TEXTO,
        )
        estilo.configure(
            "Titulo.TLabel",
            background=COR_FUNDO,
            foreground=COR_TEXTO,
            font=("Segoe UI", 15, "bold"),
        )
        estilo.configure(
            "Pergunta.TLabel",
            background=COR_PAINEL,
            foreground=COR_TEXTO,
            font=("Segoe UI", 16, "bold"),
            wraplength=560,
            justify="left",
        )
        estilo.configure(
            "Fraca.TLabel",
            background=COR_FUNDO,
            foreground=COR_TEXTO_FRACO,
            font=("Segoe UI", 9),
        )
        estilo.configure(
            "FracaPainel.TLabel",
            background=COR_PAINEL,
            foreground=COR_TEXTO_FRACO,
            font=("Segoe UI", 9),
        )
        estilo.configure(
            "TButton",
            background="#334155",
            foreground=COR_TEXTO,
            borderwidth=0,
            padding=(12, 7),
            font=("Segoe UI", 10, "bold"),
        )
        estilo.map("TButton", background=[("active", "#475569")])
        estilo.configure(
            "Destaque.TButton",
            background=COR_DESTAQUE,
            foreground="#082f49",
        )
        estilo.map("Destaque.TButton", background=[("active", "#7dd3fc")])
        estilo.configure("TNotebook", background=COR_FUNDO, borderwidth=0)
        estilo.configure(
            "TNotebook.Tab",
            background="#1e293b",
            foreground=COR_TEXTO_FRACO,
            padding=(18, 9),
            font=("Segoe UI", 10, "bold"),
        )
        estilo.map(
            "TNotebook.Tab",
            background=[("selected", COR_DESTAQUE)],
            foreground=[("selected", "#082f49")],
        )
        estilo.configure(
            "TEntry",
            fieldbackground="#0b1220",
            foreground=COR_TEXTO,
            insertcolor=COR_TEXTO,
            borderwidth=0,
            padding=6,
        )
        estilo.configure(
            "TCombobox",
            fieldbackground="#0b1220",
            background="#334155",
            foreground=COR_TEXTO,
            arrowcolor=COR_TEXTO,
            borderwidth=0,
            padding=5,
        )
        estilo.configure(
            "TSpinbox",
            fieldbackground="#0b1220",
            foreground=COR_TEXTO,
            arrowcolor=COR_TEXTO,
            borderwidth=0,
            padding=5,
        )
        estilo.configure(
            "Treeview",
            background="#0b1220",
            fieldbackground="#0b1220",
            foreground=COR_TEXTO,
            rowheight=26,
            borderwidth=0,
        )
        estilo.configure(
            "Treeview.Heading",
            background="#334155",
            foreground=COR_TEXTO,
            font=("Segoe UI", 9, "bold"),
            padding=5,
        )
        estilo.map("Treeview", background=[("selected", "#0369a1")])

    def _montar_abas(self) -> None:
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=18, pady=18)

        self.aba_partida = ttk.Frame(self.notebook, padding=16)
        self.aba_perguntas = ttk.Frame(self.notebook, padding=16)
        self.notebook.add(self.aba_partida, text="🎮 Partida")
        self.notebook.add(self.aba_perguntas, text="📝 Perguntas")

        self._montar_aba_partida()
        self._montar_aba_perguntas()

    def _montar_aba_partida(self) -> None:
        self.aba_partida.columnconfigure(0, weight=3)
        self.aba_partida.columnconfigure(1, weight=2)
        self.aba_partida.rowconfigure(1, weight=1)

        config = ttk.Frame(self.aba_partida)
        config.grid(row=0, column=0, sticky="ew", pady=(0, 14))

        ttk.Label(config, text="Jogador").grid(row=0, column=0, sticky="w")
        self.entrada_nome = ttk.Entry(config, width=20)
        self.entrada_nome.grid(row=1, column=0, padx=(0, 10), sticky="w")
        self.entrada_nome.insert(0, "Jogador 1")

        ttk.Label(config, text="Categoria").grid(row=0, column=1, sticky="w")
        self.combo_categoria = ttk.Combobox(config, width=16, state="readonly")
        self.combo_categoria.grid(row=1, column=1, padx=(0, 10), sticky="w")

        ttk.Label(config, text="Perguntas").grid(row=0, column=2, sticky="w")
        self.spin_quantidade = ttk.Spinbox(config, from_=1, to=20, width=6)
        self.spin_quantidade.set("5")
        self.spin_quantidade.grid(row=1, column=2, padx=(0, 12), sticky="w")

        ttk.Button(
            config,
            text="Iniciar partida",
            style="Destaque.TButton",
            command=self._iniciar_partida,
        ).grid(row=1, column=3, sticky="w")

        self.painel_pergunta = tk.Frame(
            self.aba_partida,
            bg=COR_PAINEL,
            highlightthickness=1,
            highlightbackground="#334155",
            padx=22,
            pady=18,
        )
        self.painel_pergunta.grid(row=1, column=0, sticky="nsew", padx=(0, 16))
        self.painel_pergunta.columnconfigure(0, weight=1)

        self.lbl_progresso = tk.Label(
            self.painel_pergunta,
            text="Pronto para começar",
            bg=COR_PAINEL,
            fg=COR_TEXTO_FRACO,
            font=("Segoe UI", 9),
            anchor="w",
        )
        self.lbl_progresso.grid(row=0, column=0, sticky="ew")

        self.lbl_tempo = tk.Label(
            self.painel_pergunta,
            text="",
            bg=COR_PAINEL,
            fg=COR_DESTAQUE,
            font=("Segoe UI", 13, "bold"),
            anchor="e",
        )
        self.lbl_tempo.grid(row=0, column=1, sticky="e")

        self.lbl_pergunta = tk.Label(
            self.painel_pergunta,
            text="Clique em “Iniciar partida” para começar.",
            bg=COR_PAINEL,
            fg=COR_TEXTO,
            font=("Segoe UI", 16, "bold"),
            wraplength=560,
            justify="left",
            anchor="w",
        )
        self.lbl_pergunta.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(18, 14))

        self.frame_alternativas = tk.Frame(self.painel_pergunta, bg=COR_PAINEL)
        self.frame_alternativas.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.alternativa_var = tk.StringVar(value="")

        self.lbl_feedback = tk.Label(
            self.painel_pergunta,
            text="",
            bg=COR_PAINEL,
            fg=COR_TEXTO,
            font=("Segoe UI", 11, "bold"),
            wraplength=560,
            justify="left",
            anchor="w",
        )
        self.lbl_feedback.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(16, 8))

        self.btn_responder = ttk.Button(
            self.painel_pergunta,
            text="Responder",
            style="Destaque.TButton",
            command=self._responder,
        )
        self.btn_responder.grid(row=4, column=0, sticky="w")

        self._montar_ranking()

    def _montar_ranking(self) -> None:
        painel = ttk.Frame(self.aba_partida, style="Painel.TFrame", padding=14)
        painel.grid(row=0, column=1, rowspan=2, sticky="nsew")
        painel.rowconfigure(1, weight=1)
        painel.columnconfigure(0, weight=1)

        ttk.Label(
            painel,
            text="🏆 Ranking",
            style="Painel.TLabel",
            font=("Segoe UI", 13, "bold"),
        ).grid(row=0, column=0, sticky="w", pady=(0, 10))

        colunas = ("nome", "pontos", "acertos", "aproveitamento")
        self.tree_ranking = ttk.Treeview(
            painel,
            columns=colunas,
            show="headings",
            height=14,
        )
        titulos = {
            "nome": ("Jogador", 130),
            "pontos": ("Pontos", 65),
            "acertos": ("Acertos", 65),
            "aproveitamento": ("%", 60),
        }
        for coluna, (titulo, largura) in titulos.items():
            self.tree_ranking.heading(coluna, text=titulo)
            self.tree_ranking.column(coluna, width=largura, anchor="center")
        self.tree_ranking.column("nome", anchor="w")
        self.tree_ranking.grid(row=1, column=0, sticky="nsew")

        ttk.Button(
            painel,
            text="Atualizar ranking",
            command=self._atualizar_ranking,
        ).grid(row=2, column=0, sticky="ew", pady=(10, 0))

    def _montar_aba_perguntas(self) -> None:
        self.aba_perguntas.columnconfigure(0, weight=1)
        self.aba_perguntas.rowconfigure(2, weight=1)

        formulario = ttk.Frame(self.aba_perguntas, style="Painel.TFrame", padding=14)
        formulario.grid(row=0, column=0, sticky="ew")
        formulario.columnconfigure(1, weight=1)
        formulario.columnconfigure(3, weight=1)

        ttk.Label(formulario, text="Enunciado", style="Painel.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.entrada_enunciado = ttk.Entry(formulario)
        self.entrada_enunciado.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(2, 10))

        self.entradas_alternativas: list[ttk.Entry] = []
        for indice in range(4):
            linha = 2 + indice // 2
            coluna = (indice % 2) * 2
            ttk.Label(
                formulario,
                text=f"Alternativa {LETRAS[indice]}",
                style="Painel.TLabel",
            ).grid(row=linha, column=coluna, sticky="w")
            entrada = ttk.Entry(formulario)
            entrada.grid(
                row=linha + 1,
                column=coluna,
                columnspan=2,
                sticky="ew",
                padx=(0, 12) if coluna == 0 else (0, 0),
                pady=(2, 10),
            )
            self.entradas_alternativas.append(entrada)

        opcoes = ttk.Frame(formulario, style="Painel.TFrame")
        opcoes.grid(row=6, column=0, columnspan=4, sticky="ew")
        for indice, texto in enumerate(
            ("Correta", "Categoria", "Dificuldade", "Tempo (s)")
        ):
            ttk.Label(opcoes, text=texto, style="Painel.TLabel").grid(
                row=0, column=indice, sticky="w", padx=(0, 10)
            )

        self.combo_correta = ttk.Combobox(
            opcoes, values=["1", "2", "3", "4"], width=5, state="readonly"
        )
        self.combo_correta.set("1")
        self.combo_correta.grid(row=1, column=0, padx=(0, 10), sticky="w")

        self.combo_categoria_nova = ttk.Combobox(
            opcoes, values=list(CATEGORIAS_PADRAO), width=14, state="readonly"
        )
        self.combo_categoria_nova.set("Geral")
        self.combo_categoria_nova.grid(row=1, column=1, padx=(0, 10), sticky="w")

        self.combo_dificuldade = ttk.Combobox(
            opcoes, values=list(DIFICULDADES), width=10, state="readonly"
        )
        self.combo_dificuldade.set("facil")
        self.combo_dificuldade.grid(row=1, column=2, padx=(0, 10), sticky="w")

        self.spin_tempo = ttk.Spinbox(opcoes, from_=5, to=120, width=6)
        self.spin_tempo.set("20")
        self.spin_tempo.grid(row=1, column=3, padx=(0, 10), sticky="w")

        ttk.Button(
            opcoes,
            text="Adicionar pergunta",
            style="Destaque.TButton",
            command=self._adicionar_pergunta,
        ).grid(row=1, column=4, sticky="w")

        ttk.Label(
            self.aba_perguntas,
            text="Perguntas cadastradas",
            style="Titulo.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(18, 8))

        colunas = ("id", "enunciado", "categoria", "dificuldade", "tempo")
        self.tree_perguntas = ttk.Treeview(
            self.aba_perguntas,
            columns=colunas,
            show="headings",
        )
        for coluna, titulo, largura, alinhamento in (
            ("id", "ID", 80, "center"),
            ("enunciado", "Enunciado", 520, "w"),
            ("categoria", "Categoria", 110, "center"),
            ("dificuldade", "Dificuldade", 100, "center"),
            ("tempo", "Tempo", 70, "center"),
        ):
            self.tree_perguntas.heading(coluna, text=titulo)
            self.tree_perguntas.column(coluna, width=largura, anchor=alinhamento)
        self.tree_perguntas.grid(row=2, column=0, sticky="nsew")

        barra = ttk.Frame(self.aba_perguntas)
        barra.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(
            barra,
            text="Atualizar lista",
            command=self._carregar_perguntas,
        ).pack(side="left")
        self.lbl_total_perguntas = ttk.Label(barra, text="", style="Fraca.TLabel")
        self.lbl_total_perguntas.pack(side="left", padx=12)

    # ------------------------------------------------------------- Partida
    def _iniciar_partida(self) -> None:
        nome = self.entrada_nome.get().strip()
        if len(nome) < 2:
            messagebox.showwarning("Nome inválido", "Informe pelo menos 2 caracteres.")
            return

        categoria = self.combo_categoria.get()
        categoria = None if categoria in ("", "Todas") else categoria

        try:
            quantidade = int(self.spin_quantidade.get())
        except ValueError:
            messagebox.showwarning("Quantidade inválida", "Use um número inteiro.")
            return

        try:
            self.partida = self.service.iniciar_partida(
                nome=nome,
                quantidade=quantidade,
                categoria=categoria,
            )
        except ValueError as erro:
            messagebox.showerror("Não foi possível iniciar", str(erro))
            return

        self._mostrar_pergunta()

    def _mostrar_pergunta(self) -> None:
        self._parar_timer()
        self.lbl_feedback.configure(text="")
        self.btn_responder.configure(state="normal", text="Responder")

        if self.partida is None:
            return

        pergunta = self.partida.pergunta_atual()
        if pergunta is None:
            self._mostrar_resumo()
            return

        self.lbl_progresso.configure(
            text=(
                f"Pergunta {self.partida.indice_atual + 1} de "
                f"{self.partida.total_perguntas} · {pergunta.categoria} · "
                f"{pergunta.dificuldade}"
            )
        )
        self.lbl_pergunta.configure(text=pergunta.enunciado)

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
                selectcolor="#0b1220",
                font=("Segoe UI", 11),
                anchor="w",
                justify="left",
                padx=6,
                pady=4,
                borderwidth=0,
                highlightthickness=0,
            ).pack(fill="x", anchor="w")

        self.tempo_restante = pergunta.tempo_limite
        self._atualizar_tempo()
        self._tick()

    def _tick(self) -> None:
        if self.partida is None or self.partida.status != "em_andamento":
            return

        self._atualizar_tempo()
        if self.tempo_restante <= 0:
            self._responder(alternativa=-1)
            return

        self.tempo_restante -= 1
        self.timer_id = self.after(1000, self._tick)

    def _atualizar_tempo(self) -> None:
        restante = max(0, self.tempo_restante)
        cor = COR_ERRO if restante <= 5 else COR_DESTAQUE
        self.lbl_tempo.configure(text=f"⏱ {restante}s", fg=cor)

    def _parar_timer(self) -> None:
        if self.timer_id is not None:
            try:
                self.after_cancel(self.timer_id)
            except tk.TclError:
                pass
            self.timer_id = None

    def _responder(self, alternativa: int | None = None) -> None:
        if self.partida is None or self.partida.status != "em_andamento":
            return

        if alternativa is None:
            escolha = self.alternativa_var.get()
            if escolha == "":
                messagebox.showinfo("Escolha uma alternativa", "Marque A, B, C ou D.")
                return
            alternativa = int(escolha)

        self._parar_timer()

        try:
            _, pergunta, resposta = self.service.responder(
                partida_id=self.partida.id,
                alternativa=alternativa,
                tempo_restante=self.tempo_restante if alternativa != -1 else 0,
            )
        except (KeyError, ValueError) as erro:
            messagebox.showerror("Erro ao responder", str(erro))
            return

        self.btn_responder.configure(state="disabled")
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

        self.lbl_feedback.configure(text=texto, fg=cor)
        self.lbl_progresso.configure(
            text=(
                f"Placar: {self.partida.jogador.pontuacao} pontos · "
                f"{self.partida.jogador.acertos} acerto(s)"
            )
        )

        if self.partida.status == "finalizada":
            self.btn_responder.configure(text="Ver resultado")
            self.btn_responder.configure(
                state="normal", command=self._mostrar_resumo
            )
            self._atualizar_ranking()
        else:
            self.after(1600, self._proxima_pergunta)

    def _proxima_pergunta(self) -> None:
        if self.partida is None or self.partida.status == "finalizada":
            return
        self.btn_responder.configure(command=self._responder)
        self._mostrar_pergunta()

    def _mostrar_resumo(self) -> None:
        self._parar_timer()
        if self.partida is None:
            return

        jogador = self.partida.jogador
        self.lbl_progresso.configure(text="Partida finalizada")
        self.lbl_tempo.configure(text="")
        self.lbl_pergunta.configure(
            text=(
                f"🏁 Fim de jogo, {jogador.nome}!\n"
                f"{jogador.pontuacao} pontos · {jogador.acertos}/"
                f"{jogador.respondidas} acertos · {jogador.aproveitamento}%"
            )
        )
        self.lbl_feedback.configure(
            text="Inicie outra partida quando quiser.",
            fg=COR_TEXTO_FRACO,
        )
        self.alternativa_var.set("")
        for widget in self.frame_alternativas.winfo_children():
            widget.destroy()
        self.btn_responder.configure(
            text="Responder", state="normal", command=self._responder
        )
        self._atualizar_ranking()

    # ------------------------------------------------------------ Ranking
    def _atualizar_ranking(self) -> None:
        for item in self.tree_ranking.get_children():
            self.tree_ranking.delete(item)

        try:
            ranking = self.service.ranking(limite=10)
        except Exception as erro:  # noqa: BLE001 - painel não deve quebrar
            messagebox.showerror("Erro no ranking", str(erro))
            return

        for posicao, jogador in enumerate(ranking, start=1):
            self.tree_ranking.insert(
                "",
                "end",
                values=(
                    f"{posicao}. {jogador.get('nome', '?')}",
                    jogador.get("pontuacao", 0),
                    jogador.get("acertos", 0),
                    f"{jogador.get('aproveitamento', 0)}%",
                ),
            )

    # ----------------------------------------------------------- Perguntas
    def _atualizar_categorias(self) -> None:
        categorias = set(CATEGORIAS_PADRAO)
        try:
            categorias.update(
                pergunta["categoria"] for pergunta in self.service.listar_perguntas()
            )
        except Exception:  # noqa: BLE001 - categorias são auxiliares
            pass

        valores = ["Todas"] + sorted(categorias)
        self.combo_categoria.configure(values=valores)
        self.combo_categoria.set("Todas")
        self.combo_categoria_nova.configure(values=sorted(categorias))

    def _adicionar_pergunta(self) -> None:
        enunciado = self.entrada_enunciado.get().strip()
        alternativas = [
            entrada.get().strip()
            for entrada in self.entradas_alternativas
            if entrada.get().strip()
        ]

        if len(enunciado) < 5:
            messagebox.showwarning(
                "Enunciado inválido", "Escreva pelo menos 5 caracteres."
            )
            return
        if len(alternativas) < 2:
            messagebox.showwarning(
                "Alternativas insuficientes", "Preencha pelo menos 2 alternativas."
            )
            return

        correta = int(self.combo_correta.get()) - 1
        if correta >= len(alternativas):
            messagebox.showwarning(
                "Resposta inválida",
                "A alternativa correta precisa estar preenchida.",
            )
            return

        try:
            tempo = int(self.spin_tempo.get())
        except ValueError:
            messagebox.showwarning("Tempo inválido", "Use um número inteiro.")
            return

        dados = {
            "enunciado": enunciado,
            "alternativas": alternativas,
            "correta": correta,
            "categoria": self.combo_categoria_nova.get() or "Geral",
            "dificuldade": self.combo_dificuldade.get() or "facil",
            "tempo_limite": tempo,
        }

        try:
            self.service.criar_pergunta(dados)
        except (ValueError, KeyError) as erro:
            messagebox.showerror("Não foi possível salvar", str(erro))
            return

        messagebox.showinfo("Pergunta adicionada", "A pergunta foi salva no JSON.")
        self._limpar_formulario_pergunta()
        self._atualizar_categorias()
        self._carregar_perguntas()

    def _limpar_formulario_pergunta(self) -> None:
        self.entrada_enunciado.delete(0, "end")
        for entrada in self.entradas_alternativas:
            entrada.delete(0, "end")
        self.combo_correta.set("1")
        self.combo_dificuldade.set("facil")
        self.spin_tempo.set("20")

    def _carregar_perguntas(self) -> None:
        for item in self.tree_perguntas.get_children():
            self.tree_perguntas.delete(item)

        try:
            perguntas = self.service.listar_perguntas(publico=False)
        except Exception as erro:  # noqa: BLE001 - painel não deve quebrar
            messagebox.showerror("Erro ao carregar perguntas", str(erro))
            return

        for pergunta in perguntas:
            self.tree_perguntas.insert(
                "",
                "end",
                values=(
                    pergunta.id,
                    pergunta.enunciado,
                    pergunta.categoria,
                    pergunta.dificuldade,
                    f"{pergunta.tempo_limite}s",
                ),
            )

        self.lbl_total_perguntas.configure(
            text=f"{len(perguntas)} pergunta(s) no arquivo data/perguntas.json"
        )


def main() -> None:
    app = AplicacaoQuiz()
    app.mainloop()


if __name__ == "__main__":
    main()
