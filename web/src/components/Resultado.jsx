import Ranking from "./Ranking";

export default function Resultado({ partida, onJogarNovamente }) {
  const jogador = partida.jogador;
  const aproveitamento = jogador.aproveitamento;

  const mensagem =
    aproveitamento >= 80
      ? "Excelente!"
      : aproveitamento >= 50
        ? "Bom trabalho!"
        : "Bora treinar mais!";

  const estatisticas = [
    { rotulo: "Pontos", valor: jogador.pontuacao, cor: "text-sky-300" },
    {
      rotulo: "Acertos",
      valor: `${jogador.acertos}/${jogador.respondidas}`,
      cor: "text-emerald-300",
    },
    {
      rotulo: "Aproveitamento",
      valor: `${aproveitamento}%`,
      cor: "text-amber-300",
    },
  ];

  return (
    <section className="space-y-6">
      <div className="rounded-3xl border border-sky-500/30 bg-gradient-to-br from-sky-500/15 to-slate-900/80 p-6 text-center shadow-2xl sm:p-10">
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-sky-300">
          Fim de jogo
        </p>

        <h2 className="mt-2 text-3xl font-black sm:text-4xl">
          {mensagem} {jogador.nome}!
        </h2>

        <p className="mt-2 text-sm text-slate-400">
          Você respondeu {jogador.respondidas} de {partida.total_perguntas}{" "}
          perguntas.
        </p>

        <div className="mt-8 grid gap-3 sm:grid-cols-3">
          {estatisticas.map((item) => (
            <div
              key={item.rotulo}
              className="rounded-2xl border border-slate-700/70 bg-slate-950/50 px-4 py-5"
            >
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                {item.rotulo}
              </p>
              <p className={`mt-1 text-3xl font-black ${item.cor}`}>
                {item.valor}
              </p>
            </div>
          ))}
        </div>

        <button
          type="button"
          onClick={onJogarNovamente}
          className="mt-8 w-full rounded-xl bg-sky-400 px-6 py-3 font-bold text-slate-950 transition hover:bg-sky-300 sm:w-auto"
        >
          Jogar novamente
        </button>
      </div>

      <Ranking limite={10} />
    </section>
  );
}
