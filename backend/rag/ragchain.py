import os
from pathlib import Path
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("OPENAI_API_KEY")
chat_model=os.getenv("AZURE_OPENAI_CHAT_MODEL")
deployment = os.getenv("AZURE_OPENAI_EMEBDDING_DEPLOYMENT")
api_version = os.getenv("AZURE_OPENAI_API_EMEBDDING_VERSION")

# Validate environment variables
if not all([deployment, azure_endpoint, api_key]):
    raise ValueError("Missing required Azure OpenAI environment variables.")


# Initialize Chroma database (path relative to this file so it works on any OS / cwd)
persist_directory = str(Path(__file__).parent / "dbchroma")

vectorstore = Chroma(
        embedding_function=AzureOpenAIEmbeddings(azure_deployment=deployment, chunk_size=16),
        persist_directory=persist_directory,
    )

# Set up retriever
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Initialize LLM
llm = AzureChatOpenAI(
    deployment_name=chat_model,
    azure_endpoint=azure_endpoint,
    api_key=api_key,
    api_version=api_version
)

# Create prompt template
prompt = ChatPromptTemplate.from_template(
    """
    You are Spark AI, a helpful assistant for company policy queries. Answer the following question based solely on the provided context, 
    which contains company policies, procedures, or regulations. If multiple documents are included in the context, synthesize the information 
    to provide a concise and accurate answer.
    
    <context>
    {context}
    </context>
    Question: {input}
    
    """
)
answer_chain = prompt | llm


def answer(query: str) -> str:
    docs = retriever.invoke(query)
    context = "\n\n".join(doc.page_content for doc in docs)
    return answer_chain.invoke({"context": context, "input": query}).content
