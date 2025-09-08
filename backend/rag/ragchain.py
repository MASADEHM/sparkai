import os
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain.chains.retrieval import  create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.question_answering import load_qa_chain
from langchain_core.documents import Document
from langchain.tools.retriever import create_retriever_tool
import os
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("OPENAI_API_KEY")
chat_model=os.getenv("AZURE_OPENAI_CHAT_MODEL")
deployment = os.getenv("AZURE_OPENAI_EMEBDDING_DEPLOYMENT")
embedding_model = os.getenv("AZURE_OPENAI_EMEBDDING_MODEL")
api_version = os.getenv("AZURE_OPENAI_API_EMEBDDING_VERSION")

# Validate environment variables
if not all([embedding_model, azure_endpoint, api_key]):
    raise ValueError("Missing required Azure OpenAI environment variables.")


# Initialize Chroma database
persist_directory = r"backend\rag\dbchroma"

vectorstore = Chroma(
        embedding_function=AzureOpenAIEmbeddings(
            deployment=os.environ["AZURE_OPENAI_EMEBDDING_DEPLOYMENT"], chunk_size=16
        ),
        persist_directory=persist_directory #os.environ["DATA_STORAGE"],  
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
    You are inventixAI, a helpful assistant for company policy queries. Answer the following question based solely on the provided context, 
    which contains company policies, procedures, or regulations. If multiple documents are included in the context, synthesize the information 
    to provide a concise and accurate answer.
    
    <context>
    {context}
    </context>
    Question: {input}
    
    """
)
# Create chains
document_chain = create_stuff_documents_chain(llm, prompt)
retrieval_chain = create_retrieval_chain(retriever, document_chain)

# Invoke the chain
# try:
#     response = retrieval_chain.invoke({"input": "What are the Performance and Discipline?"})
#     print("Answer:", response["answer"])
#     print("Retrieved Documents:", [doc.page_content for doc in response["context"]])
# except Exception as e:
#     print(f"Error: {e}")