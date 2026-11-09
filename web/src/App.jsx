import { useEffect, useState } from "react";
import Home from "./components/Home";
import Quiz from "./components/Quiz";
import Resultado from "./components/Resultado";
import Ranking from "./components/Ranking";
import { api } from "./lib/api";

export default function App() {
  const [tela, setTela] = useState("home");
  const [categorias, setCategorias] = useState([]);
  const [partida, setPartida] = useState(null);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState("");

  useEffect(() => {
    let ativo = true;

    api
      .categorias()
      .then((lista) => {
        if (ativo) setCategorias(lista);
      })
      .catch(() => {
        if (ativo) {
          setErro(
            "Não foi possível carregar as categorias. O backend está rodando em http://localhost:8000?",
          );
        }
      });

    return () => {
      ativo = false;
    };
  }, []);

  async function iniciarPartida({ nome, categoria, quantidade }) {
    setCarregando(true);
    setErro("");

    try {
      const novaPartida = await api.iniciarPartida({
        nome,
        categoria: categoria === "Todas" ? null : categoria,
        quantidade: quantidade === "Todas" ? null : Number(quantidade),
      });
      setPartida(novaPartida);
      setTela("quiz");
    } catch (falha) {
      setErro(falha.message);
    } finally {
      setCarregando(false);
    }
  }

  function finalizarPartida(partidaFinal) {
    setPartida(partidaFinal);
    setTela("resultado");
  }

  function voltarAoInicio() {
    setPartida(null);
    setErro("");
    setTela("home");
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.18),_transparent_55%)]" />

      <main className="relative mx-auto flex min-h-screen w-full max-w-5xl flex-col px-4 py-8 sm:px-6">
        <header className="mb-8 flex items-center justify-between gap-4">
          <button type="button" onClick={voltarAoInicio} className="text-left">
            <p className="text-xs font-semibold uppercase tracking-[0.35em] text-sky-400">
              Quiz Arena
            </p>
            <h1 className="text-2xl font-black sm:text-3xl">
              Mostre o que você aprendeu
            </h1>
          </button>

          <span className="hidden rounded-full border border-slate-800 bg-slate-900/70 px-4 py-2 text-xs text-slate-400 sm:block">
            Python · Web · Games · Git
          </span>
        </header>

        {erro && (
          <div className="mb-6 rounded-2xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            {erro}
          </div>
        )}

        {tela === "home" && (
          <Home
            categorias={categorias}
            carregando={carregando}
            onIniciar={iniciarPartida}
            onVerRanking={() => setTela("ranking")}
          />
        )}

        {tela === "quiz" && partida && (
          <Quiz
            partida={partida}
            onFinalizar={finalizarPartida}
            onSair={voltarAoInicio}
          />
        )}

        {tela === "resultado" && partida && (
          <Resultado partida={partida} onJogarNovamente={voltarAoInicio} />
        )}

        {tela === "ranking" && <Ranking onVoltar={voltarAoInicio} />}

        <footer className="mt-auto pt-10 text-center text-xs text-slate-600">
          Projeto em grupo · FastAPI + React + Tkinter
        </footer>
      </main>
    </div>
  );
}
