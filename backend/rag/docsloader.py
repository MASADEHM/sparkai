from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from langchain_community.vectorstores.chroma import Chroma
from dotenv import load_dotenv
import os
import glob
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load the environment variables
load_dotenv()

# Step 1: Initialize variables
docs_directory = "docs"
persist_directory = "dbchroma"

# Step 2: Collect all .txt files from the docs folder
try:
    txt_files = glob.glob(os.path.join(docs_directory, "*.pdf"))
    if not txt_files:
        logger.error(f"No .txt files found in {docs_directory}")
        raise FileNotFoundError(f"No .txt files found in {docs_directory}")
    logger.info(f"Found {len(txt_files)} text files in {docs_directory}")
except Exception as e:
    logger.error(f"Error accessing directory {docs_directory}: {e}")
    raise


# Step 3: Initialize text splitter with chunk_size
text_splitter=CharacterTextSplitter(
    separator="\n",
    chunk_size=1000, 
    chunk_overlap=100
    )

# Step 4: Initialize the PDF loader and Load and split all documents
all_docs = []
for file_path in txt_files:
    try:
        loader = PyPDFLoader(file_path)
        docs = loader.load_and_split(text_splitter=text_splitter)
        all_docs.extend(docs)
        logger.info(f"Processed file: {file_path} with {len(docs)} chunks")
    except Exception as e:
        logger.warning(f"Error processing file {file_path}: {e}")
        continue

if not all_docs:
    logger.error("No documents were successfully processed")
    raise ValueError("No documents were successfully processed")

# Step 5: Initialize the embeddings
model = os.getenv("AZURE_OPENAI_EMEBDDING_MODEL")
embeddings = AzureOpenAIEmbeddings(model=model)

# Test the embedding function
embed=embeddings.embed_query("hello world")
print(embed)

# Step 6: Initialize the vector store
db=Chroma.from_documents(
    all_docs,
    embedding=embeddings,
    persist_directory=persist_directory
    )
# Persist the database explicitly
db.persist()

# result=db.similarity_search("what are the Performance and Discipline?",k=3)

# for result in result:
#     print("\n")
#     print(result.page_content)
#     print("===================================")
#     print(result.metadata)
#     print("===================================")

# for doc in docs:
#     print(doc.metadata)
#     print(doc.page_content)
#     print("===================================")