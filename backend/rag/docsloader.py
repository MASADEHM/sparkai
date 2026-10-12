# Rebuilds the vector store from the PDFs in backend/rag/docs.
# Run from the repo root: python -m backend.rag.docsloader
from pathlib import Path
from pypdf import PdfReader
from langchain_text_splitters import CharacterTextSplitter
from backend.rag.ragchain import vectorstore
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

docs_directory = Path(__file__).parent / "docs"
pdf_files = sorted(docs_directory.glob("*.pdf"))
if not pdf_files:
    raise FileNotFoundError(f"No .pdf files found in {docs_directory}")
logger.info(f"Found {len(pdf_files)} pdf files in {docs_directory}")

text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000, chunk_overlap=100)

all_docs = []
for file_path in pdf_files:
    for page_no, page in enumerate(PdfReader(file_path).pages):
        all_docs.extend(text_splitter.create_documents(
            [page.extract_text() or ""],
            metadatas=[{"source": file_path.name, "page": page_no}],
        ))
    logger.info(f"Processed file: {file_path.name}")

if not all_docs:
    raise ValueError("No documents were successfully processed")

# Start from an empty collection so re-running doesn't store every chunk again.
vectorstore.reset_collection()
vectorstore.add_documents(all_docs)
logger.info(f"Stored {len(all_docs)} chunks")
