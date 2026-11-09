import { useCallback, useEffect, useState } from "react";
import { api } from "../lib/api";

const MEDALHAS = ["🥇", "🥈", "🥉"];

export default function Ranking({ onVoltar, limite = 10 }) {
  const [ranking, setRanking] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");

  const carregar = useCallback(async () => {
    setCarregando(true);
    setErro("");

    try {
      setRanking(await api.ranking(limite));
    } catch (falha) {
      setErro(falha.message);
    } finally {
      setCarregando(false);
    }
  }, [limite]);

  useEffect(() => {
    carregar();
  }, [carregar]);

  return (
    <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-2xl shadow-sky-950/40 backdrop-blur sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-sky-400">
            Classificação
          </p>
          <h2 className="mt-1 text-2xl font-black">🏆 Ranking</h2>
        </div>

        <button
          type="button"
          onClick={carregar}
          disabled={carregando}
          className="rounded-xl border border-slate-700 px-4 py-2 text-xs font-semibold text-slate-300 transition hover:border-sky-400/60 hover:text-sky-200 disabled:opacity-50"
        >
          {carregando ? "Atualizando..." : "Atualizar"}
        </button>
      </div>

      {erro && (
        <p className="mt-6 rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {erro}
        </p>
      )}

      {carregando && !erro && (
        <p className="mt-6 text-sm text-slate-400">Carregando ranking...</p>
      )}

      {!carregando && !erro && ranking.length === 0 && (
        <p className="mt-6 rounded-xl border border-dashed border-slate-700 px-4 py-6 text-center text-sm text-slate-400">
          Ninguém jogou ainda. Seja o primeiro a entrar na arena!
        </p>
      )}

      {ranking.length > 0 && (
        <ol className="mt-6 space-y-2">
          {ranking.map((jogador, indice) => (
            <li
              key={`${jogador.id ?? jogador.nome}-${indice}`}
              className="flex items-center gap-3 rounded-2xl border border-slate-800 bg-slate-950/50 px-4 py-3"
            >
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-slate-800/80 text-sm font-black text-slate-300">
                {MEDALHAS[indice] ?? `${indice + 1}º`}
              </span>

              <div className="min-w-0 flex-1">
                <p className="truncate font-bold text-slate-100">
                  {jogador.nome}
                </p>
                <p className="text-xs text-slate-500">
                  {jogador.acertos} acerto(s) · {jogador.aproveitamento}%
                  {jogador.partidas ? ` · ${jogador.partidas} partida(s)` : ""}
                </p>
              </div>

              <span className="text-lg font-black tabular-nums text-sky-300">
                {jogador.pontuacao}
              </span>
            </li>
          ))}
        </ol>
      )}

      {onVoltar && (
        <button
          type="button"
          onClick={onVoltar}
          className="mt-6 w-full rounded-xl bg-sky-400 px-6 py-3 font-bold text-slate-950 transition hover:bg-sky-300"
        >
          Voltar ao início
        </button>
      )}
    </section>
  );
}
