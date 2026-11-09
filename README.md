# 🎯 Quiz Arena

Aplicação de quiz criada como projeto em grupo para reunir, na prática, tudo o
que foi visto nas aulas: **Python com POO**, **Tkinter**, **Pygame**, **HTML/CSS/JS**,
**React + Vite + Tailwind**, **FastAPI**, **pytest/unittest** e **Git/GitHub**.

O jogo tem três partes que compartilham o mesmo núcleo de regras:

- **Painel desktop (Tkinter)** — o apresentador inicia partidas, vê o tempo,
  responde as perguntas e cadastra novas perguntas.
- **API (FastAPI)** — expõe perguntas, partidas e ranking em JSON.
- **Web (React)** — o jogador entra com o nome, escolhe categoria e quantidade,
  responde contra o tempo e vê o ranking.

---

## ✅ O que já funciona

- [x] Regras de domínio em POO (`Pergunta`, `Jogador`, `Partida`, `Resposta`)
- [x] Pontuação por dificuldade + bônus de tempo
- [x] Persistência em JSON (`data/perguntas.json` e `data/ranking.json`)
- [x] 20 perguntas iniciais sobre o conteúdo das aulas
- [x] API FastAPI com documentação automática em `/docs`
- [x] Testes do núcleo com `unittest` (sem dependências externas)
- [x] Testes da API com `pytest` + `TestClient`
- [x] Painel Tkinter com abas **Partida** e **Perguntas**
- [x] Interface React com Home, Quiz, Resultado e Ranking
- [x] Pipeline de CI em `.github/workflows/pipeline.yml`

---

## 🧱 Stack

| Camada | Tecnologia |
| --- | --- |
| Regras e persistência | Python 3.11+ (dataclasses, JSON) |
| API | FastAPI + Pydantic + Uvicorn |
| Testes | unittest (núcleo) e pytest (API) |
| Desktop | Tkinter |
| Web | React 18 + Vite + Tailwind CSS |
| CI | GitHub Actions |

---

## 📁 Estrutura

```text
quiz-arena/
├── .github/
│   └── workflows/
│       └── pipeline.yml
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── test_main.py
├── core/
│   ├── __init__.py
│   ├── models.py
│   ├── services.py
│   └── storage.py
├── data/
│   ├── perguntas.json
│   └── ranking.example.json
├── desktop/
│   └── painel.py
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

### 1. Backend (FastAPI)

No Windows, use Python 3.11 ou 3.13 (o Python 3.15 pode não ter as dependências):

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt

cd backend
uvicorn main:app --reload --port 8000
```

- API: <http://localhost:8000>
- Documentação interativa: <http://localhost:8000/docs>
- Health check: <http://localhost:8000/health>

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

### 4. Testes

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
| `GET` | `/api/categorias` | Lista as categorias disponíveis |
| `GET` | `/api/perguntas` | Lista perguntas (sem revelar a correta) |
| `POST` | `/api/perguntas` | Cadastra uma pergunta |
| `POST` | `/api/partidas` | Inicia uma partida |
| `GET` | `/api/partidas/{id}` | Consulta o estado da partida |
| `POST` | `/api/partidas/{id}/responder` | Responde a pergunta atual |
| `GET` | `/api/ranking?limite=10` | Retorna o ranking |

Exemplo de partida:

```json
{
  "nome": "Ana",
  "categoria": "Python",
  "quantidade": 5
}
```

Para responder, envie `{"alternativa": 2, "tempo_restante": 12}`. Use
`alternativa: -1` quando o tempo esgotar.

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

Não é necessário `package-lock.json` para o CI funcionar; o `npm install` é
executado direto.

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
- [x] API REST com FastAPI
- [x] Painel Tkinter
- [x] Front-end React
- [x] Pipeline de CI
- [ ] Modo arcade com Pygame
- [ ] Partidas multiplayer em tempo real (WebSocket)
- [ ] Migrar persistência de JSON para SQLite
- [ ] Deploy do backend e do front-end
- [ ] Tela de administração com login

---

## 🛠️ Problemas comuns

**A web mostra "Não foi possível carregar as categorias".**
O backend não está rodando. Inicie o Uvicorn na porta 8000.

**`ModuleNotFoundError: fastapi`.**
O ambiente virtual não está ativado ou foi criado com outra versão do Python.
Use `py -3.11 -m venv .venv` e ative antes de instalar.

**Porta 8000 ou 5173 ocupada.**

```powershell
uvicorn main:app --reload --port 8001
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
