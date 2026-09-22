# ingest.py - Versão Simplificada
from sentence_transformers import SentenceTransformer
import chromadb
import os
import glob
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações
DOCS_DIR = "./documentos"
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "conhecimento_agricola"

# Inicializar ChromaDB (sem função de embedding)
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

try:
    collection = chroma_client.get_collection(name=COLLECTION_NAME)
    logger.info(f"✅ Coleção '{COLLECTION_NAME}' já existe.")
except chromadb.errors.NotFoundError:
    collection = chroma_client.create_collection(name=COLLECTION_NAME)
    logger.info(f"✅ Nova coleção '{COLLECTION_NAME}' criada.")

# Função para ler PDFs
def load_pdf(file_path: str) -> str:
    try:
        import PyPDF2
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        logger.error(f"❌ Erro ao ler PDF {file_path}: {e}")
        return ""

# Função para ler TXTs
def load_txt(file_path: str) -> str:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
        except Exception as e:
            logger.error(f"❌ Erro ao ler TXT {file_path}: {e}")
            return ""

# Função para carregar documentos
def load_documents_from_folder(folder_path: str):
    documents = []

    # PDFs
    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))
    for file_path in pdf_files:
        logger.info(f"📄 Lendo PDF: {file_path}")
        text = load_pdf(file_path)
        if text and len(text.strip()) > 50:
            chunks = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 100]
            if not chunks:
                chunks = [text.strip()] if len(text.strip()) > 100 else []
            for i, chunk in enumerate(chunks):
                documents.append({
                    'id': f"{os.path.basename(file_path)}_{i}",
                    'text': chunk,
                    'metadata': {"source": os.path.basename(file_path), "type": "pdf"}
                })
            logger.info(f"   ✅ {len(chunks)} chunks criados")

    # TXTs
    txt_files = glob.glob(os.path.join(folder_path, "*.txt"))
    for file_path in txt_files:
        logger.info(f"📄 Lendo TXT: {file_path}")
        text = load_txt(file_path)
        if text and len(text.strip()) > 50:
            chunks = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 50]
            if not chunks:
                chunks = [text.strip()] if len(text.strip()) > 50 else []
            for i, chunk in enumerate(chunks):
                documents.append({
                    'id': f"{os.path.basename(file_path)}_{i}",
                    'text': chunk,
                    'metadata': {"source": os.path.basename(file_path), "type": "txt"}
                })
            logger.info(f"   ✅ {len(chunks)} chunks criados")

    return documents

# Executar ingestão
logger.info("🔄 Iniciando ingestão de documentos...")
docs_to_index = load_documents_from_folder(DOCS_DIR)

if not docs_to_index:
    logger.warning("⚠️ Nenhum documento encontrado para indexar.")
    logger.info("💡 Adicione arquivos .pdf ou .txt na pasta ./documentos")
else:
    logger.info(f"📦 {len(docs_to_index)} chunks prontos para indexar.")

    batch_size = 100
    for i in range(0, len(docs_to_index), batch_size):
        batch = docs_to_index[i:i+batch_size]
        collection.add(
            ids=[doc['id'] for doc in batch],
            documents=[doc['text'] for doc in batch],
            metadatas=[doc['metadata'] for doc in batch]
        )
        logger.info(f"✅ Indexados {len(batch)} chunks...")

    logger.info("✅ Ingestão concluída com sucesso!")

logger.info(f"📊 Total de documentos na coleção: {collection.count()}")
