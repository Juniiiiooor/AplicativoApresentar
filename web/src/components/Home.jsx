import { useState } from "react";

const QUANTIDADES = ["5", "10", "15", "20", "Todas"];

const DESTAQUES = [
  {
    icone: "⏱️",
    titulo: "Contra o tempo",
    texto: "Responda rápido para ganhar bônus de até 5 pontos por pergunta.",
  },
  {
    icone: "🏆",
    titulo: "Ranking",
    texto: "Cada partida finalizada entra no ranking salvo em JSON.",
  },
  {
    icone: "🎯",
    titulo: "Categorias",
    texto: "Escolha Python, POO, Web, React, Backend, Git, Games ou todas.",
  },
];

export default function Home({
  categorias,
  carregando,
  onIniciar,
  onVerRanking,
}) {
  const [nome, setNome] = useState("");
  const [categoria, setCategoria] = useState("Todas");
  const [quantidade, setQuantidade] = useState("10");
  const [aviso, setAviso] = useState("");

  function enviar(evento) {
    evento.preventDefault();

    if (nome.trim().length < 2) {
      setAviso("Digite um nome com pelo menos 2 caracteres.");
      return;
    }

    setAviso("");
    onIniciar({ nome: nome.trim(), categoria, quantidade });
  }

  return (
    <section className="grid gap-6 lg:grid-cols-[1.25fr_1fr]">
      <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-6 shadow-2xl shadow-sky-950/40 backdrop-blur sm:p-8">
        <span className="inline-flex rounded-full bg-sky-500/15 px-3 py-1 text-xs font-semibold text-sky-300">
          Partida rápida
        </span>

        <h2 className="mt-4 text-3xl font-black leading-tight sm:text-4xl">
          Entre na arena e responda antes do tempo acabar.
        </h2>

        <p className="mt-3 text-sm leading-relaxed text-slate-400">
          Perguntas de Python, POO, Web, React, Backend, Git e Games. Cada
          acerto vale pontos e o tempo restante dá bônus.
        </p>

        <form onSubmit={enviar} className="mt-8 space-y-5">
          <div>
            <label
              htmlFor="nome"
              className="mb-2 block text-sm font-semibold text-slate-300"
            >
              Seu nome
            </label>
            <input
              id="nome"
              value={nome}
              onChange={(evento) => setNome(evento.target.value)}
              maxLength={30}
              placeholder="Ex.: Ana Souza"
              autoComplete="off"
              className="w-full rounded-xl border border-slate-700 bg-slate-950/80 px-4 py-3 text-slate-100 outline-none transition placeholder:text-slate-600 focus:border-sky-400 focus:ring-2 focus:ring-sky-400/30"
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label
                htmlFor="categoria"
                className="mb-2 block text-sm font-semibold text-slate-300"
              >
                Categoria
              </label>
              <select
                id="categoria"
                value={categoria}
                onChange={(evento) => setCategoria(evento.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-950/80 px-4 py-3 text-slate-100 outline-none transition focus:border-sky-400 focus:ring-2 focus:ring-sky-400/30"
              >
                <option value="Todas">Todas</option>
                {categorias.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label
                htmlFor="quantidade"
                className="mb-2 block text-sm font-semibold text-slate-300"
              >
                Quantidade
              </label>
              <select
                id="quantidade"
                value={quantidade}
                onChange={(evento) => setQuantidade(evento.target.value)}
                className="w-full rounded-xl border border-slate-700 bg-slate-950/80 px-4 py-3 text-slate-100 outline-none transition focus:border-sky-400 focus:ring-2 focus:ring-sky-400/30"
              >
                {QUANTIDADES.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {aviso && <p className="text-sm text-amber-300">{aviso}</p>}

          <div className="flex flex-col gap-3 sm:flex-row">
            <button
              type="submit"
              disabled={carregando}
              className="rounded-xl bg-sky-400 px-6 py-3 font-bold text-slate-950 transition hover:bg-sky-300 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {carregando ? "Preparando partida..." : "Começar partida"}
            </button>

            <button
              type="button"
              onClick={onVerRanking}
              className="rounded-xl border border-slate-700 bg-slate-900 px-6 py-3 font-semibold text-slate-200 transition hover:border-sky-400/60 hover:text-sky-200"
            >
              Ver ranking
            </button>
          </div>
        </form>
      </div>

      <aside className="space-y-4">
        {DESTAQUES.map((item) => (
          <article
            key={item.titulo}
            className="rounded-2xl border border-slate-800 bg-slate-900/50 p-5 transition hover:border-sky-400/40 hover:bg-slate-900/80"
          >
            <p className="text-2xl">{item.icone}</p>
            <h3 className="mt-2 font-bold text-slate-100">{item.titulo}</h3>
            <p className="mt-1 text-sm leading-relaxed text-slate-400">
              {item.texto}
            </p>
          </article>
        ))}

        <p className="rounded-2xl border border-dashed border-slate-800 px-5 py-4 text-xs leading-relaxed text-slate-500">
          Dica: para jogar, o backend precisa estar rodando com{" "}
          <code className="rounded bg-slate-800 px-1 py-0.5 text-slate-300">
            uvicorn main:app --reload --port 8000
          </code>
          .
        </p>
      </aside>
    </section>
  );
}
