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

- Python 3.8+
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
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the FastAPI backend server:
```bash
cd backend
uvicorn backend.app:app --reload
Or
uvicorn app:app --reload
```
The API will be available at `http://127.0.0.1:8000`

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

- POST `/chat`: Main chat endpoint
- POST `/`: Test endpoint

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

[Your License Here]