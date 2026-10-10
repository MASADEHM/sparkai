#  AI Chat Application

A conversational AI application built with FastAPI backend and Streamlit frontend, utilizing Azure OpenAI services and RAG (Retrieval Augmented Generation) for enhanced responses.

## Project Structure
```
/
├── backend/
│   ├── rag/
│   │   ├── dbchroma/        # Chroma vector database
│   │   └── ragchain.py      # RAG implementation
│   ├── agent.py
│   └── app.py              # FastAPI server
├── chat_app.py             # Streamlit frontend
└── .env                    # Environment variables
```

## Prerequisites

- Python 3.11+
- Azure OpenAI API access
- Required Python packages (install via requirements.txt)

## Environment Setup

1. Create a `.env` file in the root directory with the following variables:
```
AZURE_OPENAI_ENDPOINT=your_azure_endpoint
OPENAI_API_KEY=your_api_key
AZURE_OPENAI_CHAT_MODEL=your_chat_model
AZURE_OPENAI_EMEBDDING_DEPLOYMENT=your_embedding_deployment
AZURE_OPENAI_EMEBDDING_MODEL=your_embedding_model
AZURE_OPENAI_API_EMEBDDING_VERSION=your_api_version
AZURE_OPENAI_API_KEY=your_api_key
OPENAI_API_VERSION=your_api_version
API_USERNAME=choose_a_username
API_PASSWORD=choose_a_password
TAVILY_API_KEY=your_tavily_key
SMTP_SERVER=your_smtp_host
SMTP_PORT=25
# Optional: if set, STARTTLS + login are used
SMTP_USER=
SMTP_PWD=
# Optional
CHECKPOINT_DB=checkpoints.sqlite
CORS_ORIGINS=*
```

To rebuild the vector store from PDFs in `backend/rag/docs/`: `python -m backend.rag.docsloader`

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the FastAPI backend server:
```bash
uvicorn backend.app:app --reload
```
The API will be available at `http://127.0.0.1:8000`

Swagger http://localhost:8000/docs

2. Start the Streamlit frontend (in a new terminal):
```bash
streamlit run chat_app.py
```
The web interface will be available at `http://localhost:8501`

## Features

- Real-time chat interface
- Integration with Azure OpenAI
- RAG-powered responses using Chroma vector database
- Session management for chat history
- Thread-based conversation tracking

## API Endpoints

All endpoints except `/health` require HTTP Basic auth (`API_USERNAME` / `API_PASSWORD`).

- GET `/health`: Health check
- POST `/chat`: Main chat endpoint
- POST `/tradename`: Trade name validation

See [API_EXAMPLES.md](API_EXAMPLES.md) for detailed usage examples and request/response formats.

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

[Your License Here]


## Deployment

### Quick Deploy with Docker Desktop

1. **Test locally:**
```bash
.\test-local.ps1
```

2. **Build and push to ACR:**
```bash
.\build-and-push.ps1
```

3. **Deploy to Azure:**
```bash
.\deploy-azure.ps1 -ResourceGroup "sparkai-rg" -AcrName "crfb01" -Location "eastus"
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide.

### Manual Deploy to ACR

```bash
# Build backend
docker build -t sparkai:1.1 .

# Login to ACR
az acr login -n crfb01.azurecr.io

# Tag and push
docker tag sparkai:1.1 crfb01.azurecr.io/sparkai:1.1
docker push crfb01.azurecr.io/sparkai:1.1
```
