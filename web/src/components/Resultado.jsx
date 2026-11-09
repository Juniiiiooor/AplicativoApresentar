import Ranking from "./Ranking";

export default function Resultado({ partida, onJogarNovamente }) {
  const jogador = partida.jogador;
  const aproveitamento = jogador.aproveitamento;
  const revisao = partida.revisao ?? [];

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

      {revisao.length > 0 && (
        <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 sm:p-8">
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-sky-400">
            Revisão
          </p>
          <h2 className="mt-1 text-2xl font-black">O que você respondeu</h2>

          <ol className="mt-5 space-y-3">
            {revisao.map((item, indice) => (
              <li
                key={`${item.pergunta_id}-${indice}`}
                className={`rounded-2xl border px-4 py-4 ${
                  item.acertou
                    ? "border-emerald-400/30 bg-emerald-500/5"
                    : "border-red-400/30 bg-red-500/5"
                }`}
              >
                <p className="font-bold text-slate-100">
                  {item.acertou ? "✅" : "❌"} {indice + 1}. {item.enunciado}
                </p>
                <p className="mt-2 text-sm text-slate-400">
                  Você marcou:{" "}
                  <span className="font-semibold text-slate-200">
                    {item.escolhida ?? "tempo esgotado"}
                  </span>
                </p>
                <p className="text-sm text-slate-400">
                  Resposta certa:{" "}
                  <span className="font-semibold text-emerald-300">
                    {item.correta}
                  </span>{" "}
                  · {item.pontos} ponto(s)
                </p>
                {item.explicacao && (
                  <p className="mt-2 text-sm text-sky-200">
                    💡 {item.explicacao}
                  </p>
                )}
              </li>
            ))}
          </ol>
        </div>
      )}

      <Ranking limite={10} />
    </section>
  );
}
