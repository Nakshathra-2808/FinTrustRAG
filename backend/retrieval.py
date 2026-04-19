import faiss
import numpy as np
import pickle
import os
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = "all-MiniLM-L6-v2"
TOP_K = 10
TOP_N = 5
RRF_K = 60
DATA_DIR = "data"

_embedder = None


def get_embedder():
    global _embedder
    if _embedder is None:
        print("🤖 Loading embedding model...")
        _embedder = SentenceTransformer(EMBEDDING_MODEL)
        print("✅ Embedding model loaded")
    return _embedder


def build_faiss_index(chunks: list, session_id: str):
    print("🔨 Building FAISS index...")
    embedder = get_embedder()
    texts = [c["text"] for c in chunks]
    embeddings = embedder.encode(texts, show_progress_bar=False)
    embeddings = np.array(embeddings).astype(np.float32)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    os.makedirs(DATA_DIR, exist_ok=True)
    faiss.write_index(index, os.path.join(DATA_DIR, f"{session_id}_faiss.index"))
    print(f"✅ FAISS index built: {index.ntotal} vectors")
    return index


def build_bm25_index(chunks: list, session_id: str):
    print("🔨 Building BM25 index...")
    tokenized = [c["text"].lower().split() for c in chunks]
    bm25 = BM25Okapi(tokenized)
    with open(os.path.join(DATA_DIR, f"{session_id}_bm25.pkl"), "wb") as f:
        pickle.dump(bm25, f)
    print("✅ BM25 index built")
    return bm25


def build_indexes(chunks: list, session_id: str):
    build_faiss_index(chunks, session_id)
    build_bm25_index(chunks, session_id)


def load_indexes(session_id: str):
    faiss_path = os.path.join(DATA_DIR, f"{session_id}_faiss.index")
    bm25_path = os.path.join(DATA_DIR, f"{session_id}_bm25.pkl")
    if not os.path.exists(faiss_path):
        raise FileNotFoundError(f"No FAISS index for session {session_id}")
    if not os.path.exists(bm25_path):
        raise FileNotFoundError(f"No BM25 index for session {session_id}")
    faiss_index = faiss.read_index(faiss_path)
    with open(bm25_path, "rb") as f:
        bm25_index = pickle.load(f)
    return faiss_index, bm25_index


def retrieve(question: str, session_id: str, chunks: list) -> list:
    print(f"🔍 Retrieving for: '{question[:50]}'")
    embedder = get_embedder()
    faiss_index, bm25_index = load_indexes(session_id)

    query_vector = np.array(
        embedder.encode([question])
    ).astype(np.float32)
    _, indices = faiss_index.search(query_vector, TOP_K)
    dense_ids = [i for i in indices[0].tolist() if i != -1]

    bm25_scores = bm25_index.get_scores(question.lower().split())
    sparse_ids = np.argsort(bm25_scores)[::-1][:TOP_K].tolist()

    scores = {}
    for rank, doc_id in enumerate(dense_ids):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (RRF_K + rank + 1)
    for rank, doc_id in enumerate(sparse_ids):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (RRF_K + rank + 1)

    fused_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    top_chunks = [chunks[i] for i in fused_ids[:TOP_N] if i < len(chunks)]
    print(f"✅ Retrieved {len(top_chunks)} chunks")
    return top_chunks