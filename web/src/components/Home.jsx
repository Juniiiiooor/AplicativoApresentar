const MODOS = [
  {
    id: "quiz",
    icone: "🎯",
    titulo: "Quiz relâmpago",
    descricao:
      "Perguntas de múltipla escolha contra o tempo. Quanto mais rápido, maior o bônus.",
    acao: "Jogar quiz",
    destaque: "border-sky-500/40 hover:border-sky-400",
    etiqueta: "bg-sky-500/15 text-sky-300",
    botao: "bg-sky-400 text-slate-950 hover:bg-sky-300",
    topicos: "Python · POO · Web · React · Git",
  },
  {
    id: "cacabug",
    icone: "🐞",
    titulo: "Caça ao Bug",
    descricao:
      "Um trecho de código com erro aparece na tela. Descubra qual correção resolve o problema.",
    acao: "Caçar bugs",
    destaque: "border-emerald-500/40 hover:border-emerald-400",
    etiqueta: "bg-emerald-500/15 text-emerald-300",
    botao: "bg-emerald-400 text-slate-950 hover:bg-emerald-300",
    topicos: "Python · React · Flask · Git",
  },
  {
    id: "ranking",
    icone: "🏆",
    titulo: "Ranking",
    descricao:
      "Veja a melhor partida de cada jogador e quantas vezes já entraram na arena.",
    acao: "Ver ranking",
    destaque: "border-amber-500/40 hover:border-amber-400",
    etiqueta: "bg-amber-500/15 text-amber-300",
    botao: "bg-amber-400 text-slate-950 hover:bg-amber-300",
    topicos: "Pontuação · Aproveitamento",
  },
];

export default function Home({ onJogarQuiz, onCacaBug, onVerRanking }) {
  const acoes = {
    quiz: onJogarQuiz,
    cacabug: onCacaBug,
    ranking: onVerRanking,
  };

  return (
    <section>
      <div className="text-center">
        <span className="inline-flex rounded-full border border-slate-700 bg-slate-900/70 px-4 py-1 text-xs font-semibold uppercase tracking-[0.25em] text-sky-300">
          Escolha um modo
        </span>
        <h2 className="mt-4 text-3xl font-black leading-tight sm:text-4xl">
          Duas formas de treinar o que você aprendeu.
        </h2>
        <p className="mx-auto mt-3 max-w-2xl text-sm leading-relaxed text-slate-400">
          Jogue o quiz tradicional ou teste seu olhar de programador no Caça ao
          Bug. O ranking guarda o melhor resultado de cada jogador.
        </p>
      </div>

      <div className="mt-10 grid gap-5 md:grid-cols-3">
        {MODOS.map((modo) => (
          <button
            key={modo.id}
            type="button"
            onClick={acoes[modo.id]}
            className={`group flex flex-col rounded-3xl border bg-slate-900/60 p-6 text-left transition hover:-translate-y-1 hover:bg-slate-900/90 ${modo.destaque}`}
          >
            <span className="text-4xl transition group-hover:scale-110">
              {modo.icone}
            </span>

            <span
              className={`mt-4 inline-flex w-fit rounded-full px-3 py-1 text-[11px] font-bold uppercase tracking-wider ${modo.etiqueta}`}
            >
              {modo.titulo}
            </span>

            <p className="mt-3 text-sm leading-relaxed text-slate-400">
              {modo.descricao}
            </p>

            <span className="mt-4 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
              {modo.topicos}
            </span>

            <span
              className={`mt-6 inline-flex items-center justify-center rounded-xl px-5 py-3 text-sm font-bold transition ${modo.botao}`}
            >
              {modo.acao} →
            </span>
          </button>
        ))}
      </div>

      <p className="mt-8 rounded-2xl border border-dashed border-slate-800 px-5 py-4 text-center text-xs leading-relaxed text-slate-400">
        Dica: a web inteira sobe junto com o backend. Abra um terminal na pasta
        do projeto, rode{" "}
        <code className="rounded bg-slate-800 px-1 py-0.5 text-slate-300">
          python main.py
        </code>{" "}
        e acesse{" "}
        <code className="rounded bg-slate-800 px-1 py-0.5 text-slate-300">
          http://127.0.0.1:8000
        </code>
        . Ao fechar o terminal, o site para de responder.
      </p>
    </section>
  );
}
