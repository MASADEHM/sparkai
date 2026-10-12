# SparkAI

A conversational AI assistant with a FastAPI backend and a Streamlit frontend. It runs on Azure OpenAI and uses LangGraph to drive a tool-calling agent, with RAG over a Chroma vector store.

## Features

- Chat with per-thread history, persisted to SQLite so it survives restarts
- Email OTP verification before the agent can use its sensitive tools
- Agent tools: company document search (RAG), web search (Tavily), email sending
- `/tradename` endpoint that validates a trade name against UAE naming rules
- HTTP Basic auth on every endpoint except `/health`
- Docker Compose setup for running backend and frontend together

## Project Structure

```text
├── backend/
│   ├── app.py              # FastAPI server
│   ├── agent.py            # Chat agent (LangGraph)
│   ├── agent_tradename.py  # Trade name validation chain
│   ├── prompts.py          # System prompts
│   ├── tools.py            # Agent tools (search, email, OTP)
│   └── rag/
│       ├── ragchain.py     # RAG chain
│       ├── docsloader.py   # Builds the vector store from PDFs
│       ├── docs/           # Source documents
│       └── dbchroma/       # Chroma vector store
├── chat_app.py             # Streamlit frontend
├── docker-compose.yml
└── .env.example            # Environment variable template
```

## Prerequisites

- Python 3.11+
- An Azure OpenAI resource with a chat deployment and an embedding deployment
- A [Tavily](https://tavily.com) API key
- An SMTP server, used to send OTP codes

## Setup

```bash
git clone <this-repo-url>
cd sparkai
cp .env.example .env        # then fill in your values
pip install -r requirements.txt
```

Every variable is described in [.env.example](.env.example).

To rebuild the vector store from the PDFs in `backend/rag/docs/`, run:

```bash
python -m backend.rag.docsloader
```

## Running

### Locally

```bash
# Backend: http://127.0.0.1:8000 (Swagger UI at /docs)
uvicorn backend.app:app --reload

# Frontend, in a second terminal: http://localhost:8501
streamlit run chat_app.py
```

### With Docker Compose

```bash
docker compose up --build
```

Docker Compose reads `.env` for both services. Chat history is stored in `./data`.

## API

All endpoints except `/health` require HTTP Basic auth using `API_USERNAME` / `API_PASSWORD`.

| Method | Path         | Description              |
|--------|--------------|--------------------------|
| GET    | `/health`    | Health check             |
| POST   | `/chat`      | Chat with the agent      |
| POST   | `/tradename` | Validate a trade name    |

Request and response examples are in [API_EXAMPLES.md](API_EXAMPLES.md).

## Deployment

The deployment guides target Azure Container Registry and Azure Container Apps. See [DEPLOYMENT.md](DEPLOYMENT.md) and [QUICKSTART.md](QUICKSTART.md).

To build and push the images by hand:

```bash
docker build -t <your-acr>.azurecr.io/sparkai-backend:latest -f Dockerfile .
docker build -t <your-acr>.azurecr.io/sparkai-frontend:latest -f Dockerfile.streamlit .
az acr login -n <your-acr>
docker push <your-acr>.azurecr.io/sparkai-backend:latest
docker push <your-acr>.azurecr.io/sparkai-frontend:latest
```

## Security

- Never commit `.env`. It is already listed in `.gitignore`.
- In production, set strong values for `API_USERNAME` and `API_PASSWORD`, and restrict `CORS_ORIGINS`.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a pull request
