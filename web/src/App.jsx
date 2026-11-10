import { useEffect, useState } from "react";
import Home from "./components/Home";
import ConfigurarQuiz from "./components/ConfigurarQuiz";
import Quiz from "./components/Quiz";
import Resultado from "./components/Resultado";
import Ranking from "./components/Ranking";
import CacaBug from "./components/CacaBug";
import { api } from "./lib/api";

const CHAVE_PARTIDA = "quiz-arena:partida";

export default function App() {
  const [tela, setTela] = useState("home");
  const [categorias, setCategorias] = useState([]);
  const [partida, setPartida] = useState(null);
  const [carregando, setCarregando] = useState(false);
  const [retomando, setRetomando] = useState(true);
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
            "Não foi possível carregar as categorias. O backend Flask está rodando em http://localhost:8000?",
          );
        }
      });

    const idSalvo = localStorage.getItem(CHAVE_PARTIDA);
    if (!idSalvo) {
      setRetomando(false);
      return () => {
        ativo = false;
      };
    }

    api
      .obterPartida(idSalvo)
      .then((salva) => {
        if (!ativo) return;
        if (salva.status === "em_andamento") {
          setPartida(salva);
          setTela("quiz");
        } else {
          localStorage.removeItem(CHAVE_PARTIDA);
        }
      })
      .catch(() => {
        if (ativo) localStorage.removeItem(CHAVE_PARTIDA);
      })
      .finally(() => {
        if (ativo) setRetomando(false);
      });

    return () => {
      ativo = false;
    };
  }, []);

  // Ao voltar ao menu (ou trocar de modo) a página recomeça no topo. Sem isso,
  // quem estava no fim de uma tela longa continuava "no meio" da Home e tinha a
  // impressão de que o botão "← Voltar ao menu" não havia funcionado.
  useEffect(() => {
    window.scrollTo({ top: 0, left: 0, behavior: "auto" });
  }, [tela]);

  async function iniciarPartida({ nome, categoria, quantidade, dificuldade }) {
    setCarregando(true);
    setErro("");

    try {
      const novaPartida = await api.iniciarPartida({
        nome,
        categoria: categoria === "Todas" ? null : categoria,
        quantidade: quantidade === "Todas" ? null : Number(quantidade),
        dificuldade: dificuldade === "Todas" ? null : dificuldade,
      });
      localStorage.setItem(CHAVE_PARTIDA, novaPartida.id);
      setPartida(novaPartida);
      setTela("quiz");
    } catch (falha) {
      setErro(falha.message);
    } finally {
      setCarregando(false);
    }
  }

  function finalizarPartida(partidaFinal) {
    localStorage.removeItem(CHAVE_PARTIDA);
    setPartida(partidaFinal);
    setTela("resultado");
  }

  function voltarAoInicio() {
    localStorage.removeItem(CHAVE_PARTIDA);
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

        {retomando && (
          <div className="rounded-3xl border border-slate-800 bg-slate-900/70 p-8 text-center text-sm text-slate-400">
            Verificando partida em andamento...
          </div>
        )}

        {!retomando && tela === "home" && (
          <Home
            onJogarQuiz={() => setTela("configurar")}
            onCacaBug={() => setTela("cacabug")}
            onVerRanking={() => setTela("ranking")}
          />
        )}

        {!retomando && tela === "configurar" && (
          <ConfigurarQuiz
            categorias={categorias}
            carregando={carregando}
            onIniciar={iniciarPartida}
            onVoltar={voltarAoInicio}
          />
        )}

        {!retomando && tela === "cacabug" && (
          <CacaBug onVoltar={voltarAoInicio} />
        )}

        {!retomando && tela === "quiz" && partida && (
          <Quiz
            partida={partida}
            onFinalizar={finalizarPartida}
            onSair={voltarAoInicio}
          />
        )}

        {!retomando && tela === "resultado" && partida && (
          <Resultado partida={partida} onJogarNovamente={voltarAoInicio} />
        )}

        {!retomando && tela === "ranking" && (
          <Ranking onVoltar={voltarAoInicio} />
        )}

        <footer className="mt-auto pt-10 text-center text-xs text-slate-600">
          Projeto em grupo · Flask + React + Tkinter
        </footer>
      </main>
    </div>
  );
}
