# rag.py - builds the vector index from data/knowledge_base and retrieves passages
import chromadb
from chromadb.config import Settings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import KB_DIR, CHROMA_DIR, TOP_K, MAX_DISTANCE


def get_client():
    """Local vector store. Chroma's anonymous usage telemetry is switched off so nothing leaves the computer (NFR1)."""
    return chromadb.PersistentClient(path=str(CHROMA_DIR), settings=Settings(anonymized_telemetry=False))


def get_collection():
    return get_client().get_or_create_collection("guidelines", metadata={"hnsw:space": "cosine"})


def read_kb_file(path):
    """Each file starts with TITLE:, ORG:, URL: lines, then a blank line, then the text."""
    header, body = {}, []
    in_header = True
    for line in path.read_text(encoding="utf-8").splitlines():
        if in_header and ":" in line and line.split(":", 1)[0] in ("TITLE", "ORG", "URL"):
            key, value = line.split(":", 1)
            header[key] = value.strip()
        elif in_header and line.strip() == "":
            in_header = False
        else:
            in_header = False
            body.append(line)
    return header, "\n".join(body).strip()


def build_index():
    """Clean -> chunk -> store with source details. Run again whenever the knowledge base changes."""
    client = get_client()
    try:
        client.delete_collection("guidelines")
    except Exception:
        pass
    col = client.get_or_create_collection("guidelines", metadata={"hnsw:space": "cosine"})
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)

    ids, docs, metas = [], [], []
    for path in sorted(KB_DIR.glob("*.txt")):
        header, body = read_kb_file(path)
        for i, chunk in enumerate(splitter.split_text(body)):
            ids.append(f"{path.stem}-{i}")
            docs.append(chunk)
            metas.append({"doc_id": path.stem, "title": header.get("TITLE", path.stem),
                          "org": header.get("ORG", ""), "url": header.get("URL", "")})
    if docs:
        col.add(ids=ids, documents=docs, metadatas=metas)
    return len(docs)


def retrieve(question: str):
    """Returns only passages that are close enough to the question. Empty list = system should decline."""
    col = get_collection()
    if col.count() == 0:
        return []
    res = col.query(query_texts=[question], n_results=TOP_K)
    passages = []
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        if dist <= MAX_DISTANCE:
            passages.append({"text": doc, "distance": round(dist, 3), **meta})
    for n, p in enumerate(passages, start=1):
        p["sid"] = f"S{n}"
    return passages
