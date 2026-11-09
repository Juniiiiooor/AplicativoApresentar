import { useCallback, useEffect, useState } from "react";
import { api } from "../lib/api";

const LETRAS = ["A", "B", "C", "D"];

function classesDaAlternativa(indice, feedback) {
  if (!feedback) {
    return "border-slate-700 bg-slate-950/60 hover:border-emerald-400/70 hover:bg-emerald-500/10";
  }
  if (indice === feedback.alternativa_correta) {
    return "border-emerald-400/70 bg-emerald-500/15 text-emerald-100";
  }
  if (indice === feedback.alternativa_escolhida) {
    return "border-red-400/70 bg-red-500/15 text-red-100";
  }
  return "border-slate-800 bg-slate-950/40 text-slate-500";
}

export default function CacaBug({ onVoltar }) {
  const [desafios, setDesafios] = useState([]);
  const [indice, setIndice] = useState(0);
  const [feedback, setFeedback] = useState(null);
  const [acertos, setAcertos] = useState(0);
  const [pontos, setPontos] = useState(0);
  const [enviando, setEnviando] = useState(false);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [finalizado, setFinalizado] = useState(false);

  useEffect(() => {
    let ativo = true;

    api
      .desafios()
      .then((lista) => {
        if (ativo) setDesafios(lista);
      })
      .catch((falha) => {
        if (ativo) setErro(falha.message);
      })
      .finally(() => {
        if (ativo) setCarregando(false);
      });

    return () => {
      ativo = false;
    };
  }, []);

  const desafio = desafios[indice];

  const responder = useCallback(
    async (alternativa) => {
      if (!desafio || feedback || enviando) return;

      setEnviando(true);
      setErro("");

      try {
        const dados = await api.responderDesafio(desafio.id, alternativa);
        setFeedback(dados);
        if (dados.correta) {
          setAcertos((valor) => valor + 1);
          setPontos((valor) => valor + dados.pontos);
        }
      } catch (falha) {
        setErro(falha.message);
      } finally {
        setEnviando(false);
      }
    },
    [desafio, feedback, enviando],
  );

  const avancar = useCallback(() => {
    if (!feedback) return;

    if (indice + 1 >= desafios.length) {
      setFinalizado(true);
      return;
    }

    setIndice((valor) => valor + 1);
    setFeedback(null);
    setErro("");
  }, [feedback, indice, desafios.length]);

  function reiniciar() {
    setIndice(0);
    setFeedback(null);
    setAcertos(0);
    setPontos(0);
    setErro("");
    setFinalizado(false);
  }

  useEffect(() => {
    function aoPressionar(evento) {
      if (evento.repeat) return;
      const alvo = evento.target;
      if (alvo && ["INPUT", "TEXTAREA", "SELECT"].includes(alvo.tagName)) {
        return;
      }

      if (feedback) {
        if (evento.key === "Enter" || evento.key === " ") {
          evento.preventDefault();
          avancar();
        }
        return;
      }

      if (!desafio) return;

      const atalhos = {
        "1": 0,
        "2": 1,
        "3": 2,
        "4": 3,
        a: 0,
        b: 1,
        c: 2,
        d: 3,
      };
      const escolhida = atalhos[evento.key.toLowerCase()];
      if (escolhida !== undefined && escolhida < desafio.alternativas.length) {
        evento.preventDefault();
        responder(escolhida);
      }
    }

    window.addEventListener("keydown", aoPressionar);
    return () => window.removeEventListener("keydown", aoPressionar);
  }, [feedback, desafio, responder, avancar]);

  if (carregando) {
    return (
      <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-8 text-center text-sm text-slate-400">
        Carregando desafios...
      </section>
    );
  }

  if (erro && desafios.length === 0) {
    return (
      <section className="rounded-3xl border border-red-500/40 bg-red-500/10 p-8 text-center">
        <p className="text-sm text-red-200">{erro}</p>
        <button
          type="button"
          onClick={onVoltar}
          className="mt-4 rounded-xl bg-slate-800 px-5 py-2 text-sm font-semibold text-slate-100"
        >
          Voltar ao menu
        </button>
      </section>
    );
  }

  if (desafios.length === 0) {
    return (
      <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-8 text-center">
        <p className="text-slate-400">
          Nenhum desafio cadastrado em{" "}
          <code className="rounded bg-slate-800 px-1 py-0.5 text-slate-300">
            data/desafios.json
          </code>
          .
        </p>
        <button
          type="button"
          onClick={onVoltar}
          className="mt-4 rounded-xl bg-sky-400 px-5 py-2 font-bold text-slate-950"
        >
          Voltar ao menu
        </button>
      </section>
    );
  }

  if (finalizado) {
    const aproveitamento = Math.round((acertos / desafios.length) * 100);

    return (
      <section className="rounded-3xl border border-emerald-500/30 bg-gradient-to-br from-emerald-500/15 to-slate-900/80 p-6 text-center shadow-2xl sm:p-10">
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-emerald-300">
          Fim dos desafios
        </p>
        <h2 className="mt-2 text-3xl font-black sm:text-4xl">
          {acertos} de {desafios.length} bugs encontrados!
        </h2>

        <div className="mx-auto mt-8 grid max-w-lg gap-3 sm:grid-cols-3">
          {[
            { rotulo: "Pontos", valor: pontos, cor: "text-sky-300" },
            {
              rotulo: "Acertos",
              valor: `${acertos}/${desafios.length}`,
              cor: "text-emerald-300",
            },
            {
              rotulo: "Aproveitamento",
              valor: `${aproveitamento}%`,
              cor: "text-amber-300",
            },
          ].map((item) => (
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

        <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
          <button
            type="button"
            onClick={reiniciar}
            className="rounded-xl bg-emerald-400 px-6 py-3 font-bold text-slate-950 transition hover:bg-emerald-300"
          >
            Jogar de novo
          </button>
          <button
            type="button"
            onClick={onVoltar}
            className="rounded-xl border border-slate-700 bg-slate-900 px-6 py-3 font-semibold text-slate-200 transition hover:border-emerald-400/60 hover:text-emerald-200"
          >
            Voltar ao menu
          </button>
        </div>
      </section>
    );
  }

  const progresso = Math.round(((indice + 1) / desafios.length) * 100);

  return (
    <section className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-2xl shadow-emerald-950/40 backdrop-blur sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <button
            type="button"
            onClick={onVoltar}
            className="text-xs font-semibold text-slate-400 transition hover:text-emerald-300"
          >
            ← Voltar ao menu
          </button>
          <p className="mt-2 text-xs font-semibold uppercase tracking-[0.3em] text-emerald-400">
            Caça ao Bug · {indice + 1} de {desafios.length}
          </p>
        </div>

        <span className="rounded-full bg-emerald-500/15 px-4 py-2 text-sm font-black tabular-nums text-emerald-300">
          {pontos} pts · {acertos} acerto(s)
        </span>
      </div>

      <div className="mt-4 h-2 overflow-hidden rounded-full bg-slate-800">
        <div
          className="h-full rounded-full bg-gradient-to-r from-emerald-400 to-sky-400 transition-all"
          style={{ width: `${progresso}%` }}
        />
      </div>

      <div className="mt-6 flex flex-wrap items-center gap-2">
        <span className="rounded-full bg-slate-800 px-3 py-1 text-xs font-bold text-slate-300">
          {desafio.linguagem}
        </span>
        <span className="rounded-full bg-slate-800 px-3 py-1 text-xs font-semibold text-slate-400">
          {desafio.tema}
        </span>
      </div>

      <h2 className="mt-3 text-xl font-black leading-snug sm:text-2xl">
        {desafio.titulo}
      </h2>

      <pre className="mt-4 overflow-x-auto rounded-2xl border border-slate-700/70 bg-slate-950/90 p-4 text-sm leading-relaxed text-emerald-200">
        <code>{desafio.codigo}</code>
      </pre>

      <p className="mt-4 text-sm leading-relaxed text-slate-300">
        {desafio.descricao}
      </p>

      <div className="mt-5 grid gap-3">
        {desafio.alternativas.map((alternativa, escolha) => (
          <button
            key={`${desafio.id}-${escolha}`}
            type="button"
            disabled={Boolean(feedback) || enviando}
            onClick={() => responder(escolha)}
            className={`flex items-start gap-3 rounded-2xl border px-4 py-4 text-left text-sm font-semibold transition disabled:cursor-default ${classesDaAlternativa(
              escolha,
              feedback,
            )}`}
          >
            <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-slate-800/80 text-xs font-black">
              {LETRAS[escolha] ?? escolha + 1}
            </span>
            <span className="whitespace-pre-wrap pt-0.5">{alternativa}</span>
          </button>
        ))}
      </div>

      <p className="mt-4 text-center text-xs text-slate-500">
        Atalhos: A–D ou 1–4 para responder · Enter para avançar
      </p>

      {erro && (
        <p className="mt-4 rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-200">
          {erro}
        </p>
      )}

      {feedback && (
        <div aria-live="polite">
          <div
            className={`mt-6 rounded-2xl border px-4 py-4 text-sm font-semibold ${
              feedback.correta
                ? "border-emerald-400/40 bg-emerald-500/10 text-emerald-200"
                : "border-amber-400/40 bg-amber-500/10 text-amber-200"
            }`}
          >
            {feedback.correta
              ? `✅ Bug encontrado! +${feedback.pontos} pontos`
              : `❌ Ainda não. A correção certa era: ${
                  desafio.alternativas[feedback.alternativa_correta]
                }`}
          </div>

          {feedback.explicacao && (
            <p className="mt-3 rounded-xl border border-sky-500/30 bg-sky-500/10 px-4 py-3 text-sm text-sky-100">
              💡 {feedback.explicacao}
            </p>
          )}

          <button
            type="button"
            onClick={avancar}
            className="mt-5 w-full rounded-xl bg-emerald-400 px-6 py-3 font-bold text-slate-950 transition hover:bg-emerald-300"
          >
            {indice + 1 >= desafios.length
              ? "Ver resultado"
              : "Próximo desafio"}
          </button>
        </div>
      )}
    </section>
  );
}
