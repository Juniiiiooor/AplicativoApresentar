# 📚 Aprendizados do projeto

Este documento liga cada conteúdo visto nas aulas a um lugar concreto do
código. Use como roteiro de apresentação.

## 1. Python com POO

| Conceito | Onde está |
| --- | --- |
| Classes e dataclasses | `core/models.py` (`Pergunta`, `Jogador`, `Partida`, `Resposta`) |
| Encapsulamento de regras | `Pergunta.pontos`, `Partida.responder`, `Jogador.registrar_resposta` |
| Validação no construtor | `__post_init__` de `Pergunta` e `Jogador` |
| Composição | `Partida` contém `Jogador`, `Pergunta` e `Resposta` |
| Exceções de domínio | `ConflitoDeResposta` e `ValueError` |
| Propriedades calculadas | `Jogador.aproveitamento`, `Partida.progresso`, `Partida.numero_pergunta` |

## 2. Persistência em JSON

| Conceito | Onde está |
| --- | --- |
| Leitura e escrita de arquivos | `core/storage.py` |
| Escrita atômica | `_escrever` grava `.tmp` e faz `replace` |
| Serialização | `para_dict` / `de_dict` nos modelos |
| Concorrência | `threading.Lock` em `adicionar_pergunta` e `registrar_no_ranking` |
| Ranking agregado | melhor partida por jogador, sem duplicar nomes |

## 3. API com Flask

| Conceito | Onde está |
| --- | --- |
| Rotas REST | `backend/main.py` |
| Validação manual do corpo | funções de checagem no `POST /api/perguntas` |
| Códigos HTTP | `201`, `400`, `401`, `404`, `409`, `422` |
| CORS | `adicionar_cabecalhos_cors` |
| Autenticação opcional | cabeçalho `X-Admin-Token` |
| Separação de camadas | a API só chama `QuizService` |

## 4. Testes

| Conceito | Onde está |
| --- | --- |
| Testes unitários com `unittest` | `tests/test_core.py` |
| Testes de API com `pytest` | `backend/test_main.py` |
| Isolamento com pasta temporária | `QUIZ_DATA_DIR` nos testes |
| Casos de borda | tempo esgotado, alternativa inválida, resposta repetida |
| CI | `.github/workflows/pipeline.yml` |

## 5. Tkinter

| Conceito | Onde está |
| --- | --- |
| Janela principal | classe `AplicacaoQuiz` em `desktop/painel.py` |
| Abas | `ttk.Notebook` com **Partida** e **Perguntas** |
| Formulários | `ttk.Entry`, `ttk.Combobox`, `ttk.Spinbox` |
| Listagem | `ttk.Treeview` de perguntas e ranking |
| Temporizador | `self.after(1000, self._tick)` |
| Controle do apresentador | botão **Próxima pergunta** em vez de avanço automático |

## 6. React + Vite + Tailwind

| Conceito | Onde está |
| --- | --- |
| Componentes | `web/src/components/` |
| Menu de cards | `Home.jsx` com os modos Quiz, Caça ao Bug e Ranking |
| Estado | `useState` em `App.jsx`, `Quiz.jsx`, `CacaBug.jsx` e `ConfigurarQuiz.jsx` |
| Efeitos | contagem regressiva e atalhos de teclado em `Quiz.jsx` e `CacaBug.jsx` |
| Chamadas HTTP | `web/src/lib/api.js` |
| Estilização | classes Tailwind em todos os componentes |
| Build | `vite.config.js` e `npm run build` |
| Retomada | `localStorage` em `App.jsx` |

## 7. HTML, CSS e JavaScript

| Conceito | Onde está |
| --- | --- |
| HTML base | `web/index.html` |
| CSS global | `web/src/index.css` |
| JavaScript moderno | `async/await`, `fetch`, desestruturação, módulos ES |
| Acessibilidade | `aria-live`, atalhos de teclado e foco visível |

## 8. Git e GitHub

| Conceito | Onde está |
| --- | --- |
| Branches por frente | `feat/core-backend`, `feat/desktop`, `feat/web` |
| Commits pequenos | histórico do repositório |
| CI | GitHub Actions |
| Templates | `.github/ISSUE_TEMPLATE/` e `pull_request_template.md` |
| Dependabot | `.github/dependabot.yml` |

## 9. Pygame

| Conceito | Onde está |
| --- | --- |
| Inicialização e loop | `arcade/quiz_arcade.py` |
| Janela e desenho | `pygame.display.set_mode`, `pygame.draw.rect` |
| Texto | `pygame.font.SysFont` e quebra manual de linha |
| Eventos e teclado | `pygame.event.get`, atalhos 1–4 / A–D |
| Tempo | `pygame.time.get_ticks` |
| Reuso do núcleo | as perguntas vêm de `RepositorioJSON` e a pontuação de `Pergunta.pontos` |

O modo arcade é uma alternativa visual ao quiz web, pensada para o telão da
apresentação. Ele usa as mesmas perguntas e regras do jogo principal.

## 10. Caça ao Bug (segundo modo de jogo)

| Conceito | Onde está |
| --- | --- |
| Modelo de domínio | `Desafio` em `core/models.py` |
| Dados | `data/desafios.json` (12 desafios) |
| Persistência | `carregar_desafios` / `adicionar_desafio` em `core/storage.py` |
| Regras | `responder_desafio` em `core/services.py` |
| Rotas | `GET /api/desafios` e `POST /api/desafios/{id}/responder` |
| Tela | `web/src/components/CacaBug.jsx` |
| Menu | cards em `web/src/components/Home.jsx` |
| Testes | `TestDesafio` no núcleo e casos em `backend/test_main.py` |

Esse modo reaproveita a mesma arquitetura do quiz: o `core/` valida as regras,
o Flask expõe JSON e o React apenas apresenta. A correção e a explicação só
aparecem **depois** da resposta, igual ao quiz.

## 11. Roteiro de apresentação (5 minutos)

1. Abrir o painel Tkinter e mostrar o cadastro de pergunta.
2. Iniciar uma partida no painel e explicar a pontuação.
3. Abrir a web e mostrar o menu de cards (Quiz, Caça ao Bug, Ranking).
4. Jogar uma partida curta e mostrar a explicação e a revisão.
5. Abrir o Caça ao Bug e resolver um desafio de código.
6. Mostrar o ranking agregado, os testes rodando e o pipeline no GitHub Actions.
7. Fechar com a arquitetura: `core/` compartilhado por Flask, Tkinter e arcade.
