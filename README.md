# 🎯 Quiz Arena

Aplicação de quiz criada como projeto em grupo para reunir, na prática, tudo o
que foi visto nas aulas: **Python com POO**, **Tkinter**, **Pygame**, **HTML/CSS/JS**,
**React + Vite + Tailwind**, **Flask**, **pytest/unittest** e **Git/GitHub**.

O projeto tem várias frentes que compartilham o mesmo núcleo de regras:

- **App desktop único (Tkinter)** — `desktop/app.py` abre um menu de cards com
  **Quiz relâmpago**, **Caça ao Bug** e **Ranking**, funcionando offline pelo
  `core/`, sem backend nem navegador.
- **Painel do apresentador (Tkinter)** — inicia partidas, vê o tempo, responde
  as perguntas, controla o avanço e cadastra novas perguntas.
- **API (Flask)** — expõe perguntas, partidas, desafios e ranking em JSON e
  também entrega a web compilada.
- **Web (React)** — a Home funciona como um **menu de cards**: o jogador escolhe
  entre o **Quiz relâmpago**, o **Caça ao Bug** e o **Ranking**.
- **Arcade (Pygame)** — versão com visual de fliperama usando as mesmas perguntas.

O **Caça ao Bug** é o segundo modo de jogo: aparece um trecho de código com um
erro e o jogador escolhe qual correção resolve o problema. Cada desafio vale 10
pontos e mostra uma explicação depois da resposta.

---

## ⬇️ Baixar o aplicativo (Windows)

Se você só quer jogar no Windows, sem instalar Python nem abrir o navegador:

1. Baixe **[Quiz-Arena-Windows.zip](https://github.com/Juniiiiooor/Quiz--e--bug/raw/main/downloads/Quiz-Arena-Windows.zip)**.
2. Extraia a pasta.
3. Dê duplo clique em **`Quiz Arena.exe`**.

O app abre offline com os modos **Quiz relâmpago**, **Caça ao Bug** e **Ranking**.
O ranking fica salvo em `data/ranking.json`, ao lado do `.exe`.

> Se o Windows exibir o aviso do SmartScreen, clique em **Mais informações →
> Executar assim mesmo**. O executável não é assinado digitalmente.

Para rodar a versão web, use o `python main.py` explicado mais abaixo.

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
- [x] App desktop único (Tkinter) com menu de cards e modos offline
- [x] Interface React com Home (cards), Quiz, Resultado, Ranking e Caça ao Bug
- [x] `python main.py` sobe web + API em um único processo/porta
- [x] Licença MIT em português (`LICENSE`)
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
│   ├── app.py             # app único (menu de cards, offline)
│   └── painel.py
├── docs/
│   └── aprendizados.md
├── downloads/
│   └── Quiz-Arena-Windows.zip   # app desktop pronto para baixar
├── tests/
│   ├── __init__.py
│   └── test_core.py
├── main.py                # sobe web + API com um comando
├── Quiz Arena.bat         # atalho para abrir o app desktop
├── web/
│   ├── dist/              # build servido pelo main.py
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

### 1. Aplicação completa (web + API) — um comando

No Windows, use Python 3.11 ou 3.13 (o Python 3.15 pode não ter as dependências):

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt

# a partir da raiz do projeto
python main.py
```

Esse único comando:

- sobe a API Flask;
- entrega o front-end React já compilado (`web/dist`) na mesma porta;
- abre o navegador em <http://127.0.0.1:8000>;
- mantém **um único processo**: ao fechar o terminal (ou pressionar
  **CTRL+C**), o site para de responder.

> A web só funciona enquanto `python main.py` estiver aberto. Se `web/dist`
> não existir, rode uma vez `cd web; npm install; npm run build`.

Endereços:

- Web + API: <http://127.0.0.1:8000>
- Documentação simples: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>

Também funciona entrando na pasta `backend` (`python main.py`), mas aí o
front-end só é servido se `web/dist` existir.

Variáveis opcionais:

| Variável | Efeito |
| --- | --- |
| `QUIZ_ADMIN_TOKEN` | Exige o cabeçalho `X-Admin-Token` no `POST /api/perguntas` |
| `QUIZ_CORS_ORIGINS` | Origens permitidas, separadas por vírgula (padrão: `localhost:5173`) |
| `QUIZ_DATA_DIR` | Pasta alternativa para `perguntas.json` e `ranking.json` |
| `PORT` | Porta do servidor Flask (padrão: `8000`) |
| `QUIZ_ABRIR_NAVEGADOR` | `0` impede a abertura automática do navegador |
| `QUIZ_DEBUG` | `1` liga o modo de depuração do Flask |

### 2. Modo desenvolvimento (React + Vite)

Para editar o React com recarregamento automático, rode o Vite em outro
terminal:

```powershell
cd web
npm install
npm run dev
```

Abra <http://localhost:5173>. O Vite encaminha `/api` e `/health` para
`http://127.0.0.1:8000` (veja `web/vite.config.js`), então mantenha o
`python main.py` rodando em outro terminal.

Depois de alterar o React, gere o build que o `python main.py` serve:

```powershell
cd web
npm run build
```

### 3. Apps desktop (Tkinter)

App único com menu de cards (Quiz relâmpago, Caça ao Bug e Ranking), funcionando
**offline** direto pelo `core/`:

```powershell
python desktop/app.py
```

Painel do apresentador (abas Partida e Perguntas):

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

## 🌿 Branch principal

Todo o projeto está consolidado na branch **`main`**. Para atualizar:

```powershell
git switch main
git pull origin main
```

As antigas branches de trabalho (`feat/core-backend`, `feat/desktop`,
`feat/web`, `feat/melhorias`) já foram integradas e podem ser removidas.

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
O servidor não está rodando. Na raiz do projeto, rode `python main.py` e abra
<http://127.0.0.1:8000>. Se você estiver usando o modo desenvolvimento, o Vite
(<http://localhost:5173>) também precisa do `python main.py` em outro terminal.

**Fechei o terminal, mas a web continua abrindo.**
A versão atual usa `use_reloader=False`, então `python main.py` é um único
processo e para junto com o terminal. Se ainda houver algo na porta 8000 ou
5173, encerre processos antigos:

```powershell
Get-NetTCPConnection -LocalPort 8000,5173 -State Listen |
  Select-Object LocalPort,OwningProcess
Stop-Process -Id <PID> -Force
```

**Alterei o React e a web em 8000 não mudou.**
O `python main.py` serve o build em `web/dist`. Rode `cd web; npm run build`
para atualizar (ou use o Vite em <http://localhost:5173> durante o desenvolvimento).

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
