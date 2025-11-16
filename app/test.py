# test.py
from chromadb import PersistentClient

PERSIST_DIRECTORY = "./chroma_db"
client = PersistentClient(path=PERSIST_DIRECTORY)

collection = client.get_or_create_collection(name="codebase_embeddings")

data = collection.get(limit=10)  # Get first 10 chunks
print(f"Total chunks in collection: {len(data.get('ids', []))}")

for doc, meta in zip(data.get("documents", []), data.get("metadatas", [])):
    print(meta, doc[:50], "...")
