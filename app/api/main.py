# main.py - Versão Simplificada e Funcional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
import logging
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configurações ---
LLAMA_SERVER_URL = os.getenv("LLAMA_SERVER_URL", "http://127.0.0.1:8080/v1")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "conhecimento_agricola")
TOP_K_RETRIEVALS = int(os.getenv("TOP_K_RETRIEVALS", "3"))

app = FastAPI(title="API RAG Agrícola")


# 🔧 CONFIGURAÇÃO CORS - Permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",   # Live Server (VS Code)
        "http://localhost:5500",    # Live Server (VS Code)
        "http://127.0.0.1:8000",   # Própria API
        "http://localhost:8000",    # Própria API
        "http://127.0.0.1:3000",   # React/Next.js
        "http://localhost:3000",    # React/Next.js
        "*",                        # 🔧 Permite todas (apenas para desenvolvimento)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # 🔧 Incluir OPTIONS
    allow_headers=["*"],
)

# --- Modelos de Dados ---
class QueryRequest(BaseModel):
    pergunta: str
    top_k: Optional[int] = TOP_K_RETRIEVALS

class QueryResponse(BaseModel):
    pergunta: str
    resposta: str
    fontes: List[str] = []

# --- Inicialização do ChromaDB com função de embedding simplificada ---
collection = None

try:
    import chromadb
    from sentence_transformers import SentenceTransformer

    # 🔧 SIMPLIFICADO: Função de embedding como classe simples
    class SimpleEmbedding:
        def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
            logger.info(f"✅ Modelo de embedding carregado: {model_name}")

        def __call__(self, texts):
            """Gera embeddings para os textos fornecidos."""
            if not texts:
                return []
            # Converter para lista de floats
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()

    # 🔧 Usar a função de embedding com o nome correto
    embedding_fn = SimpleEmbedding()

    # Inicializar ChromaDB
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    # 🔧 CORREÇÃO: Criar a coleção SEM a função de embedding primeiro
    try:
        # Tentar obter a coleção existente
        collection = chroma_client.get_collection(name=COLLECTION_NAME)
        logger.info(f"✅ Coleção '{COLLECTION_NAME}' encontrada.")
    except chromadb.errors.NotFoundError:
        # Criar nova coleção
        collection = chroma_client.create_collection(name=COLLECTION_NAME)
        logger.info(f"✅ Nova coleção '{COLLECTION_NAME}' criada.")

    # Verificar documentos
    if collection:
        count = collection.count()
        logger.info(f"📊 Coleção tem {count} documentos.")
        if count == 0:
            logger.warning("⚠️ A coleção está vazia! Execute 'python ingest.py' para indexar documentos.")

except Exception as e:
    logger.error(f"❌ Erro ao inicializar ChromaDB: {e}")
    collection = None

# --- Função de Busca ---
def buscar_contexto(pergunta: str, top_k: int = TOP_K_RETRIEVALS):
    """Busca documentos relevantes no ChromaDB."""
    if collection is None:
        logger.warning("⚠️ ChromaDB não inicializado.")
        return [], []

    try:
        # 🔧 Usar a função de embedding diretamente na consulta
        results = collection.query(
            query_texts=[pergunta],
            n_results=top_k
        )

        documentos = results['documents'][0] if results.get('documents') else []
        metadados = results['metadatas'][0] if results.get('metadatas') else []

        logger.info(f"✅ Encontrados {len(documentos)} documentos relevantes.")
        return documentos, metadados

    except Exception as e:
        logger.error(f"❌ Erro na busca: {e}")
        return [], []

# --- Função para Gerar Resposta ---
def gerar_resposta(pergunta: str, contexto: str) -> str:
    """Gera resposta usando o modelo com prompt bem formatado."""

    if contexto and len(contexto.strip()) > 10:
        prompt = f"""You are an assistant specializing in agriculture.
Use the context below to answer the question. If the answer is not in the context, answer the question below using your general knowledge, but only if it is related with agriculture, otherwise just say "Seems like this question does not relate with agriculture".
or "I did not find anything on my knowledge base related to this question" without making up information.
Context:
{contexto}

Question: {pergunta}
Answer:"""
    else:
        prompt = f"""You are an assistant specializing in agriculture.
Answer the question below using your general knowledge, but only if it is related with agriculture, otherwise just say "Seems like this question does not relate with agriculture".

Question: {pergunta}
Answer:"""

    payload = {
        "prompt": prompt,
        "n_predict": 256,
        "temperature": 0.3,
        "top_p": 0.9,
        "stop": ["\n\n", "Pergunta:", "Contexto:"],
        "echo": False
    }

    try:
        response = requests.post(
            f"{LLAMA_SERVER_URL}/completions",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        texto = result.get("choices", [{}])[0].get("text", "").strip()

        if "Resposta:" in texto:
            texto = texto.split("Resposta:")[-1].strip()

        return texto if texto else "Sorry, I could not generate an answer."

    except requests.exceptions.Timeout:
        logger.error("⏱️ Timeout ao chamar o llama-server")
        return "Desculpe, a geração da resposta demorou muito."
    except requests.exceptions.ConnectionError:
        logger.error("🔌 Erro de conexão com o llama-server")
        return "Desculpe, não foi possível conectar ao servidor do modelo."
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro ao chamar o llama-server: {e}")
        return f"Erro: {str(e)}"

# --- Endpoint da API ---
@app.post("/perguntar", response_model=QueryResponse)
async def perguntar(request: QueryRequest):
    pergunta = request.pergunta.strip()
    top_k = request.top_k or TOP_K_RETRIEVALS

    if not pergunta or len(pergunta) < 3:
        raise HTTPException(status_code=400, detail="Pergunta muito curta.")

    try:
        docs, metadados = buscar_contexto(pergunta, top_k)
        contexto = "\n\n".join(docs) if docs else ""
        resposta = gerar_resposta(pergunta, contexto)

        fontes = []
        for meta in metadados:
            fonte = meta.get("source", "Fonte desconhecida")
            if fonte not in fontes:
                fontes.append(fonte)

        return QueryResponse(pergunta=pergunta, resposta=resposta, fontes=fontes)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}")
        raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

# --- Health Check ---
@app.get("/health")
async def health_check():
    status = {
        "status": "ok",
        "chromadb": "conectado" if collection else "desconectado",
        "documentos": collection.count() if collection else 0,
        "llama_server": "unknown"
    }

    try:
        response = requests.get(f"{LLAMA_SERVER_URL}/health", timeout=5)
        status["llama_server"] = "online" if response.status_code == 200 else "offline"
    except:
        status["llama_server"] = "offline"

    return status

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
