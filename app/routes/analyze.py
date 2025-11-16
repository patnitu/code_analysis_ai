# app/routes/analyze.py
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.embeddings import chroma_client, collection
from app.services.code_analysis_agent import CodeAnalysisAgent
from typing import Optional

router = APIRouter()

# Initialize the RAG agent using the same ChromaDB directory
agent = CodeAnalysisAgent(
    persist_directory="./chroma_db",
    collection_name="codebase_embeddings"
)


# ----------------------
# Endpoint: List stored code chunks
# ----------------------
@router.get("/list_chunks")
def list_chunks(limit: int = 10):
    """
    List first N stored code chunks with metadata.
    """
    data = collection.get(limit=limit)
    chunks_info = []
    for doc, meta in zip(data.get("documents", []), data.get("metadatas", [])):
        chunks_info.append({
            "file": meta.get("file"),
            "chunk_id": meta.get("chunk_id"),
            "snippet": doc[:100]  # first 100 characters
        })
    return {"total_chunks": len(data.get("ids", [])), "chunks": chunks_info}


# ----------------------
# Endpoint: Query the codebase with RAG
# ----------------------
class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5


@router.post("/query")
def query_codebase(request: QueryRequest):
    """
    Retrieve relevant code chunks from ChromaDB and ask LLM to extract structured knowledge.
    """
    result = agent.extract_knowledge(request.query, top_k=request.top_k)
    return result
