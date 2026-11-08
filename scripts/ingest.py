# Rebuild the ChromaDB index from data/knowledge_base/*.txt
# usage (from the project root):  python -m scripts.ingest
from backend.app.rag import build_index

if __name__ == "__main__":
    n = build_index()
    print(f"Indexed {n} chunks.")
