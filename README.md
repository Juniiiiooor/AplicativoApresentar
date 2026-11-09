# 🎯 Quiz Arena

Aplicação de quiz criada como projeto em grupo para reunir, na prática, tudo o
que foi visto nas aulas: **Python com POO**, **Tkinter**, **Pygame**, **HTML/CSS/JS**,
**React + Vite + Tailwind**, **Flask**, **pytest/unittest** e **Git/GitHub**.

O jogo tem três partes que compartilham o mesmo núcleo de regras:

- **Painel desktop (Tkinter)** — o apresentador inicia partidas, vê o tempo,
  responde as perguntas, controla o avanço e cadastra novas perguntas.
- **API (Flask)** — expõe perguntas, partidas, desafios e ranking em JSON.
- **Web (React)** — a Home funciona como um **menu de cards**: o jogador escolhe
  entre o **Quiz relâmpago**, o **Caça ao Bug** e o **Ranking**.

O **Caça ao Bug** é o segundo modo de jogo: aparece um trecho de código com um
erro e o jogador escolhe qual correção resolve o problema. Cada desafio vale 10
pontos e mostra uma explicação depois da resposta.

---

## ✅ O que já funciona

- [x] Regras de domínio em POO (`Pergunta`, `Jogador`, `Partida`, `Resposta`)
- [x] Pontuação por dificuldade + bônus de tempo
- [x] Persistência em JSON (`data/perguntas.json`, `data/desafios.json` e `data/ranking.json`)
- [x] 20 perguntas iniciais sobre o conteúdo das aulas
- [x] **Caça ao Bug**: 12 desafios de código com correção e explicação
- [x] Home com menu de cards separando Quiz, Caça ao Bug e Ranking
- [x] API Flask com documentação simples em `/docs`
- [x] Tempo calculado no **servidor** (o cliente não consegue inflar o bônus)
- [x] Resposta idempotente com `pergunta_id` (reenvio não pula pergunta)
- [x] Ranking agregado por jogador (melhor partida, sem nomes duplicados)
- [x] Explicação da resposta e revisão final
- [x] Filtro por categoria e por dificuldade
- [x] Retomada de partida após atualizar a página (`localStorage`)
- [x] Atalhos de teclado A–D / 1–4 e feedback acessível (`aria-live`)
- [x] **Modo arcade com Pygame** usando as mesmas perguntas do núcleo
- [x] Testes do núcleo com `unittest` (sem dependências externas)
- [x] Testes da API com `pytest` + cliente de testes do Flask
- [x] Painel Tkinter com abas **Partida** e **Perguntas**
- [x] Interface React com Home (cards), Quiz, Resultado, Ranking e Caça ao Bug
- [x] Pipeline de CI em `.github/workflows/pipeline.yml`

---

## 🧱 Stack

| Camada | Tecnologia |
| --- | --- |
| Regras e persistência | Python 3.11+ (dataclasses, JSON, `threading.Lock`) |
| API | Flask 3 |
| Testes | unittest (núcleo) e pytest (API) |
| Desktop | Tkinter |
| Arcade | Pygame |
| Web | React 18 + Vite + Tailwind CSS |
| CI | GitHub Actions |

---

## 📁 Estrutura

```text
quiz-arena/
├── .github/
│   └── workflows/
│       └── pipeline.yml
├── arcade/
│   ├── quiz_arcade.py     # modo arcade com Pygame
│   └── requirements.txt
├── backend/
│   ├── main.py            # app Flask
│   ├── requirements.txt
│   └── test_main.py
├── core/
│   ├── __init__.py
│   ├── models.py
│   ├── services.py
│   └── storage.py
├── data/
│   ├── desafios.json
│   ├── perguntas.json
│   └── ranking.example.json
├── desktop/
│   └── painel.py
├── docs/
│   └── aprendizados.md
├── tests/
│   ├── __init__.py
│   └── test_core.py
├── web/
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       ├── index.css
│       ├── main.jsx
│       ├── components/
│       │   ├── CacaBug.jsx
│       │   ├── ConfigurarQuiz.jsx
│       │   ├── Home.jsx
│       │   ├── Quiz.jsx
│       │   ├── Ranking.jsx
│       │   └── Resultado.jsx
│       └── lib/
│           └── api.js
├── .gitignore
└── README.md
```

---

## 🚀 Como rodar

> Todos os comandos abaixo partem da pasta `quiz-arena`.

### 1. Backend (Flask)

No Windows, use Python 3.11 ou 3.13 (o Python 3.15 pode não ter as dependências):

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt

cd backend
python main.py
```

Alternativa com o comando do Flask:

```powershell
cd backend
flask --app main run --debug --port 8000
```

- API: <http://localhost:8000>
- Documentação simples: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>

Variáveis opcionais:

| Variável | Efeito |
| --- | --- |
| `QUIZ_ADMIN_TOKEN` | Exige o cabeçalho `X-Admin-Token` no `POST /api/perguntas` |
| `QUIZ_CORS_ORIGINS` | Origens permitidas, separadas por vírgula (padrão: `localhost:5173`) |
| `QUIZ_DATA_DIR` | Pasta alternativa para `perguntas.json` e `ranking.json` |
| `PORT` | Porta do servidor Flask (padrão: `8000`) |

### 2. Web (React + Vite)

Em outro terminal:

```powershell
cd web
npm install
npm run dev
```

Abra <http://localhost:5173>. O Vite já encaminha `/api` e `/health` para
`http://localhost:8000` (veja `web/vite.config.js`).

Para gerar a versão de produção:

```powershell
npm run build
npm run preview
```

### 3. Painel desktop (Tkinter)

```powershell
python desktop/painel.py
```

No Linux, se o Tkinter não estiver instalado: `sudo apt install python3-tk`.

### 4. Modo arcade (Pygame)

```powershell
pip install -r arcade/requirements.txt
python arcade/quiz_arcade.py
```

Controles: **1–4** ou **A–D** para responder, **Enter/Espaço** para avançar,
**R** para reiniciar e **Esc** para sair.

### 5. Testes

Núcleo (somente biblioteca padrão):

```powershell
python -m unittest discover -s tests -v
```

API (com o ambiente virtual ativo):

```powershell
cd backend
pytest -q
```

---

## 🔌 Endpoints da API

| Método | Rota | Descrição |
| --- | --- | --- |
| `GET` | `/health` | Verifica se a API está no ar |
| `GET` | `/docs` | Página simples com as rotas |
| `GET` | `/api/categorias` | Lista as categorias disponíveis |
| `GET` | `/api/perguntas` | Lista perguntas (sem revelar a correta) |
| `POST` | `/api/perguntas` | Cadastra uma pergunta |
| `GET` | `/api/desafios` | Lista os desafios do Caça ao Bug (sem a correção) |
| `POST` | `/api/desafios` | Cadastra um desafio |
| `POST` | `/api/desafios/{id}/responder` | Corrige uma resposta do Caça ao Bug |
| `POST` | `/api/partidas` | Inicia uma partida |
| `GET` | `/api/partidas/{id}` | Consulta o estado da partida |
| `POST` | `/api/partidas/{id}/responder` | Responde a pergunta atual |
| `GET` | `/api/ranking?limite=10` | Retorna o ranking agregado por jogador |

Exemplo de partida:

```json
{
  "nome": "Ana",
  "categoria": "Python",
  "quantidade": 5,
  "dificuldade": "medio"
}
```

Para responder, envie:

```json
{
  "alternativa": 2,
  "tempo_restante": 12,
  "pergunta_id": "q07"
}
```

Use `alternativa: -1` quando o tempo esgotar. O `tempo_restante` é apenas
informativo: o servidor recalcula o tempo para impedir fraude. Se o
`pergunta_id` não for o da pergunta atual, a API responde **409** em vez de
avançar duas perguntas.

Para cadastrar uma pergunta com explicação:

```json
{
  "enunciado": "Qual palavra-chave cria uma classe em Python?",
  "alternativas": ["def", "class", "object", "new"],
  "correta": 1,
  "categoria": "Python",
  "dificuldade": "facil",
  "tempo_limite": 20,
  "explicacao": "A palavra-chave class inicia a definição de uma classe."
}
```

Para responder um desafio do Caça ao Bug:

```json
{
  "alternativa": 0
}
```

A resposta devolve `correta`, `alternativa_correta`, `pontos` (10 quando acerta)
e a `explicacao`. Para cadastrar um desafio novo:

```json
{
  "titulo": "Atributo que não fica no objeto",
  "linguagem": "Python",
  "tema": "POO",
  "codigo": "class Aluno:\n    def __init__(self, nome):\n        nome = nome",
  "descricao": "O nome não fica salvo no objeto. Qual linha corrige?",
  "alternativas": ["self.nome = nome", "self.nome == nome"],
  "correta": 0,
  "explicacao": "Atributos de instância usam self."
}
```

Se `QUIZ_ADMIN_TOKEN` estiver definido, inclua o cabeçalho:

```text
X-Admin-Token: seu-token
```

---

## 🌿 Branches do grupo

O trabalho está separado em três branches, que devem ser integradas na `main`
nesta ordem:

1. `feat/core-backend` — núcleo, dados, API e testes.
2. `feat/desktop` — painel Tkinter.
3. `feat/web` — interface React e integração final.

```powershell
git switch main
git merge feat/core-backend
git merge feat/desktop
git merge feat/web
git push origin main
```

A branch `feat/web` contém todo o projeto, então é a melhor para visualizar a
versão completa antes do merge.

---

## ⚙️ Pipeline (GitHub Actions)

O arquivo `.github/workflows/pipeline.yml` roda em `push`, `pull_request` e
manualmente (`workflow_dispatch`). Ele tem três jobs:

- **core** — roda `python -m unittest discover -s tests -v` e checa a sintaxe do painel.
- **backend** — instala `backend/requirements.txt` e roda `pytest`.
- **web** — instala as dependências e roda `npm run build`.

---

## 👥 Divisão sugerida (4 a 5 pessoas)

| Pessoa | Frente | Arquivos principais |
| --- | --- | --- |
| 1 | Regras e persistência | `core/models.py`, `core/storage.py`, `tests/` |
| 2 | API e integração | `core/services.py`, `backend/` |
| 3 | Interface web | `web/src/` |
| 4 | Painel desktop | `desktop/painel.py` |
| 5 | Dados, CI e apresentação | `data/`, `.github/`, `README.md` |

---

## 🗺️ Roadmap

- [x] Estrutura inicial e regras do jogo
- [x] API REST com Flask
- [x] Painel Tkinter
- [x] Front-end React
- [x] Pipeline de CI
- [x] Tempo no servidor, idempotência, ranking agregado e revisão
- [x] Modo arcade com Pygame
- [x] Caça ao Bug com desafios de código e menu de cards
- [ ] Partidas multiplayer em tempo real (WebSocket)
- [ ] Migrar persistência de JSON para SQLite
- [ ] Deploy do backend e do front-end
- [ ] Tela de administração com login

---

## 🛠️ Problemas comuns

**A web mostra "Não foi possível carregar as categorias".**
O backend não está rodando. Inicie o Flask na porta 8000 com
`cd backend; python main.py`.

**`ModuleNotFoundError: flask`.**
O ambiente virtual não está ativado ou foi criado com outra versão do Python.
Use `py -3.11 -m venv .venv` e ative antes de instalar.

**Porta 8000 ou 5173 ocupada.**

```powershell
cd backend
$env:PORT = "8001"
python main.py
```

Nesse caso, ajuste o proxy em `web/vite.config.js`.

**`npm install` sem internet.**
Conecte-se à rede liberada e rode novamente. Se já houver cache local, tente
`npm install --prefer-offline`.

**O `data/ranking.json` não aparece no Git.**
Ele é gerado em tempo de execução e está no `.gitignore`. O modelo versionado é
`data/ranking.example.json`.

---

## 🔗 Repositório

```text
git@github.com:Juniiiiooor/AplicativoApresentar.git
```

Projeto acadêmico — use à vontade para estudar, adaptar e apresentar. 🎓
