
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

# Keywords that should boost specific section types.
# Expanded to cover Microsoft, Tesla, and other companies
# which use slightly different terminology than Apple.
SECTION_BOOST_MAP = {
    # Cash Flow triggers
    "free cash flow":           "Cash Flow",
    "fcf":                      "Cash Flow",
    "operating cash":           "Cash Flow",
    "capital expenditure":      "Cash Flow",
    "capex":                    "Cash Flow",
    "purchases of property":    "Cash Flow",
    "investing activities":     "Cash Flow",
    "financing activities":     "Cash Flow",
    "cash flow":                "Cash Flow",
    "property plant":           "Cash Flow",

    # Income Statement triggers
    "net income":               "Income Statement",
    "gross margin":             "Income Statement",
    "gross profit margin":      "Income Statement",
    "revenue":                  "Income Statement",
    "net sales":                "Income Statement",
    "total revenue":            "Income Statement",
    "net revenue":              "Income Statement",
    "earnings per share":       "Income Statement",
    "operating income":         "Income Statement",
    "net profit margin":        "Income Statement",
    "cost of revenue":          "Income Statement",
    "cost of goods":            "Income Statement",
    "operating expenses":       "Income Statement",
    "gross profit":             "Income Statement",
    "net profit":               "Income Statement",

    # Balance Sheet triggers
    "total assets":             "Balance Sheet",
    "liabilities":              "Balance Sheet",
    "return on equity":         "Balance Sheet",
    "shareholders equity":      "Balance Sheet",
    "stockholders equity":      "Balance Sheet",
    "shareholders' equity":     "Balance Sheet",
    "stockholders' equity":     "Balance Sheet",
    "long-term debt":           "Balance Sheet",
    "current assets":           "Balance Sheet",
    "current liabilities":      "Balance Sheet",
    "total equity":             "Balance Sheet",
    "debt to equity":           "Balance Sheet",
    "current ratio":            "Balance Sheet",

    # EPS triggers
    "diluted earnings":         "EPS",
    "basic earnings":           "EPS",
    "diluted shares":           "EPS",
    "weighted average":         "EPS",
}


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
    faiss.write_index(
        index,
        os.path.join(DATA_DIR, f"{session_id}_faiss.index")
    )
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


def get_section_boost(question: str, chunk: dict) -> float:
    """
    Boost score for chunks whose section_label matches
    what the question is asking about.

    WHY: BM25 matches on keywords like "cash" or "flow"
    which appear throughout the document. This ensures
    actual Cash Flow statement chunks rank above prose
    sections that merely mention cash flow in passing.
    """
    question_lower = question.lower()
    for keyword, target_section in SECTION_BOOST_MAP.items():
        if keyword in question_lower:
            if chunk.get("section_label") == target_section:
                return 0.02
    return 0.0


def force_include_section(question: str, chunks: list) -> list:
    """
    For formula queries, force-include at least one chunk
    from the relevant financial statement section even if
    RRF didn't rank it in the top 5.

    WHY: FCF verification needs the Cash Flow chunk.
    If it ranks 6th, the math verifier silently fails.
    This guarantees the right chunk is always present.
    """
    question_lower = question.lower()

    # Determine which section is required
    required_section = None
    cf_keywords = [
        "free cash flow", "fcf", "operating cash",
        "capital expenditure", "capex"
    ]
    income_keywords = [
        "gross margin", "net margin", "profit margin",
        "operating income", "net income", "revenue",
        "earnings per share", "eps", "net profit"
    ]
    balance_keywords = [
        "total assets", "return on equity", "roe",
        "debt to equity", "current ratio", "shareholders equity"
    ]

    if any(k in question_lower for k in cf_keywords):
        required_section = "Cash Flow"
    elif any(k in question_lower for k in income_keywords):
        required_section = "Income Statement"
    elif any(k in question_lower for k in balance_keywords):
        required_section = "Balance Sheet"

    return required_section


def retrieve(question: str, session_id: str, chunks: list) -> list:
    print(f"🔍 Retrieving for: '{question[:50]}'")
    embedder = get_embedder()
    faiss_index, bm25_index = load_indexes(session_id)

    # Dense retrieval
    query_vector = np.array(
        embedder.encode([question])
    ).astype(np.float32)
    _, indices = faiss_index.search(query_vector, TOP_K)
    dense_ids = [i for i in indices[0].tolist() if i != -1]

    # Sparse retrieval
    bm25_scores = bm25_index.get_scores(question.lower().split())
    sparse_ids = np.argsort(bm25_scores)[::-1][:TOP_K].tolist()

    # RRF fusion
    scores = {}
    for rank, doc_id in enumerate(dense_ids):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (RRF_K + rank + 1)
    for rank, doc_id in enumerate(sparse_ids):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (RRF_K + rank + 1)

    # Section label boost
    for doc_id in scores:
        if doc_id < len(chunks):
            scores[doc_id] += get_section_boost(question, chunks[doc_id])

    fused_ids = sorted(
        scores.keys(),
        key=lambda x: scores[x],
        reverse=True
    )
    top_chunks = [chunks[i] for i in fused_ids[:TOP_N] if i < len(chunks)]

    # Force-include required section chunk if missing
    required_section = force_include_section(question, chunks)
    if required_section:
        section_labels = [c.get("section_label") for c in top_chunks]
        if required_section not in section_labels:
            # Find the best-ranked chunk of the required section
            # that isn't already in top_chunks
            top_ids = set(c["chunk_id"] for c in top_chunks)
            for doc_id in fused_ids:
                if doc_id < len(chunks):
                    candidate = chunks[doc_id]
                    if (candidate.get("section_label") == required_section
                            and candidate["chunk_id"] not in top_ids):
                        # Replace lowest-ranked top chunk with this one
                        top_chunks[-1] = candidate
                        print(f"   ⚡ Force-included {required_section} chunk "
                              f"(page {candidate.get('page_no')})")
                        break

    print(f"✅ Retrieved {len(top_chunks)} chunks from sections: "
          f"{[c['section_label'] for c in top_chunks]}")
    return top_chunks