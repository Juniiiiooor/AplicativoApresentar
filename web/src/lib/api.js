const BASE_URL = import.meta.env.VITE_API_URL ?? "";

async function request(path, options = {}) {
  const resposta = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers ?? {}) },
    ...options,
  });

  if (!resposta.ok) {
    let detalhe = `Erro ${resposta.status}`;
    try {
      const corpo = await resposta.json();
      if (Array.isArray(corpo.detail)) {
        detalhe = corpo.detail.map((item) => item.msg).join(", ");
      } else if (corpo.detail) {
        detalhe = corpo.detail;
      }
    } catch {
      // A resposta de erro pode não ser JSON.
    }
    throw new Error(detalhe);
  }

  return resposta.json();
}

export const api = {
  health: () => request("/health"),

  categorias: () => request("/api/categorias"),

  perguntas: (categoria) =>
    request(
      `/api/perguntas${
        categoria ? `?categoria=${encodeURIComponent(categoria)}` : ""
      }`,
    ),

  iniciarPartida: ({ nome, categoria, quantidade, dificuldade }) =>
    request("/api/partidas", {
      method: "POST",
      body: JSON.stringify({ nome, categoria, quantidade, dificuldade }),
    }),

  obterPartida: (partidaId) => request(`/api/partidas/${partidaId}`),

  responder: (partidaId, alternativa, tempoRestante, perguntaId) =>
    request(`/api/partidas/${partidaId}/responder`, {
      method: "POST",
      body: JSON.stringify({
        alternativa,
        tempo_restante: tempoRestante,
        pergunta_id: perguntaId,
      }),
    }),

  ranking: (limite = 10) => request(`/api/ranking?limite=${limite}`),

  desafios: () => request("/api/desafios"),

  responderDesafio: (desafioId, alternativa) =>
    request(`/api/desafios/${desafioId}/responder`, {
      method: "POST",
      body: JSON.stringify({ alternativa }),
    }),
};
