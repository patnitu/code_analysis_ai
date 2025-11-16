# app/services/embeddings.py

import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from chromadb import PersistentClient
from app.services import code_processor

# ----------------------
# Load environment variables
# ----------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY  # Ensure OpenAI key is available

# ----------------------
# Initialize ChromaDB (persistent)
# ----------------------
PERSIST_DIRECTORY = "./chroma_db"
chroma_client = PersistentClient(path=PERSIST_DIRECTORY)

# Get or create collection
collection = chroma_client.get_or_create_collection(name="codebase_embeddings")
print(f"[DEBUG] Collection ready: {collection.name}")

# ----------------------
# Initialize OpenAI embeddings
# ----------------------
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small", api_key=OPENAI_API_KEY)

# ----------------------
# Function to store embeddings
# ----------------------
def store_embeddings(code_files):
    """
    Generate embeddings for each code chunk and store in ChromaDB.
    code_files: list of dicts, each dict with keys 'path' and 'content'
    """
    total_chunks = 0

    for file in code_files:
        print(f"[DEBUG] Processing file: {file['path']}")
        chunks = code_processor.chunk_code(file["content"])
        print(f"[DEBUG] Number of chunks for {file['path']}: {len(chunks)}")

        for idx, chunk in enumerate(chunks):
            try:
                # Generate embedding
                embedding_vector = embeddings_model.embed_documents([chunk])

                # Store in ChromaDB
                collection.add(
                    documents=[chunk],
                    metadatas={"file": file["path"], "chunk_id": idx},
                    ids=[f"{file['path']}_{idx}"],
                    embeddings=embedding_vector
                )
                total_chunks += 1
                print(f"[DEBUG] Stored chunk {idx} of {file['path']}")
            except Exception as e:
                print(f"[ERROR] Error storing chunk {idx} of {file['path']}: {e}")

    print(f"[DEBUG] Total chunks stored in this run: {total_chunks}")
