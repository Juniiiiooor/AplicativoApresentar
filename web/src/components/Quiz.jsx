import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../lib/api";

const LETRAS = ["A", "B", "C", "D", "E", "F"];

function classesDaAlternativa(indice, feedback) {
  if (!feedback) {
    return "border-slate-700 bg-slate-950/60 hover:border-sky-400/70 hover:bg-sky-500/10";
  }
  if (indice === feedback.alternativa_correta) {
    return "border-emerald-400/70 bg-emerald-500/15 text-emerald-100";
  }
  if (indice === feedback.alternativa_escolhida) {
    return "border-red-400/70 bg-red-500/15 text-red-100";
  }
  return "border-slate-800 bg-slate-950/40 text-slate-500";
}

export default function Quiz({ partida: partidaInicial, onFinalizar, onSair }) {
  const [partida, setPartida] = useState(partidaInicial);
  const [feedback, setFeedback] = useState(null);
  const [tempo, setTempo] = useState(
    partidaInicial.pergunta_atual?.tempo_limite ?? 20,
  );
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");

  const enviandoRef = useRef(false);
  const autoEnviadoRef = useRef(false);

  const pergunta = partida.pergunta_atual;
  const respondida = feedback !== null;

  const responder = useCallback(
    async (alternativa) => {
      if (!pergunta || respondida || enviandoRef.current) return;

      enviandoRef.current = true;
      setEnviando(true);
      setErro("");

      try {
        const dados = await api.responder(
          partida.id,
          alternativa,
          alternativa === -1 ? 0 : tempo,
        );
        setFeedback(dados);
      } catch (falha) {
        setErro(falha.message);
        enviandoRef.current = false;
      } finally {
        setEnviando(false);
      }
    },
    [partida.id, pergunta, respondida, tempo],
  );

  useEffect(() => {
    if (!pergunta || respondida) return undefined;

    setTempo(pergunta.tempo_limite);
    autoEnviadoRef.current = false;

    const intervalo = setInterval(() => {
      setTempo((atual) => (atual > 0 ? atual - 1 : 0));
    }, 1000);

    return () => clearInterval(intervalo);
  }, [pergunta?.id, respondida]);

  useEffect(() => {
    if (
      tempo === 0 &&
      pergunta &&
      !respondida &&
      !enviandoRef.current &&
      !autoEnviadoRef.current
    ) {
      autoEnviadoRef.current = true;
      responder(-1);
    }
  }, [tempo, pergunta, respondida, responder]);

  function avancar() {
    if (!feedback) return;

    if (feedback.partida.status === "finalizada") {
      onFinalizar(feedback.partida);
      return;
    }

    enviandoRef.current = false;
    autoEnviadoRef.current = false;
    setErro("");
    setFeedback(null);
    setPartida(feedback.partida);
  }

  if (!pergunta) {
    return (
      <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-8 text-center">
        <p className="text-slate-400">Não há pergunta disponível.</p>
        <button
          type="button"
          onClick={onSair}
          className="mt-4 rounded-xl bg-sky-400 px-5 py-2 font-bold text-slate-950"
        >
          Voltar ao início
        </button>
      </section>
    );
  }

  const percentual = Math.max(
    0,
    Math.min(100, (tempo / pergunta.tempo_limite) * 100),
  );
  const tempoCritico = tempo <= 5;
  const respostaCorreta =
    feedback &&
    feedback.pergunta_respondida.alternativas[feedback.alternativa_correta];

  return (
    <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-2xl shadow-sky-950/40 backdrop-blur sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.3em] text-sky-400">
            {partida.jogador.nome}
          </p>
          <p className="mt-1 text-sm text-slate-400">
            Pergunta {partida.progresso} · {pergunta.categoria} ·{" "}
            {pergunta.dificuldade}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <span
            className={`rounded-full px-4 py-2 text-sm font-black tabular-nums ${
              tempoCritico
                ? "bg-red-500/15 text-red-300"
                : "bg-sky-500/15 text-sky-300"
            }`}
          >
            ⏱ {tempo}s
          </span>
          <button
            type="button"
            onClick={onSair}
            className="rounded-full border border-slate-700 px-4 py-2 text-xs font-semibold text-slate-400 transition hover:border-red-400/60 hover:text-red-300"
          >
            Sair
          </button>
        </div>
      </div>

      <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-800">
        <div
          className={`h-full rounded-full transition-all duration-1000 ${
            tempoCritico
              ? "bg-gradient-to-r from-red-500 to-amber-400"
              : "bg-gradient-to-r from-sky-400 to-emerald-400"
          }`}
          style={{ width: `${percentual}%` }}
        />
      </div>

      <h2 className="mt-8 text-xl font-black leading-snug sm:text-2xl">
        {pergunta.enunciado}
      </h2>

      <div className="mt-6 grid gap-3">
        {pergunta.alternativas.map((alternativa, indice) => (
          <button
            key={`${pergunta.id}-${indice}`}
            type="button"
            disabled={respondida || enviando}
            onClick={() => responder(indice)}
            className={`flex items-start gap-3 rounded-2xl border px-4 py-4 text-left text-sm font-semibold transition disabled:cursor-default ${classesDaAlternativa(
              indice,
              feedback,
            )}`}
          >
            <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-slate-800/80 text-xs font-black">
              {LETRAS[indice] ?? indice + 1}
            </span>
            <span className="pt-0.5">{alternativa}</span>
          </button>
        ))}
      </div>

      {erro && (
        <p className="mt-5 rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {erro}
        </p>
      )}

      {feedback && (
        <div
          className={`mt-6 rounded-2xl border px-4 py-4 text-sm font-semibold ${
            feedback.correta
              ? "border-emerald-400/40 bg-emerald-500/10 text-emerald-200"
              : "border-amber-400/40 bg-amber-500/10 text-amber-200"
          }`}
        >
          {feedback.correta
            ? `✅ Correto! +${feedback.pontos} pontos`
            : feedback.alternativa_escolhida === -1
              ? `⏰ Tempo esgotado! A resposta certa era: ${respostaCorreta}`
              : `❌ Quase! A resposta certa era: ${respostaCorreta}`}
        </div>
      )}

      {feedback && (
        <button
          type="button"
          onClick={avancar}
          className="mt-5 w-full rounded-xl bg-sky-400 px-6 py-3 font-bold text-slate-950 transition hover:bg-sky-300"
        >
          {feedback.partida.status === "finalizada"
            ? "Ver resultado"
            : "Próxima pergunta"}
        </button>
      )}
    </section>
  );
}
