

# ingestion.py
# ONE JOB: Read PDF → Split into chunks → Save to disk

import pymupdf4llm
import os
import pickle

# ── SETTINGS ──────────────────────────────────────
CHUNK_SIZE = 500      # words per chunk
CHUNK_OVERLAP = 50    # words shared between chunks
DATA_DIR = "data"     # folder to save processed chunks
# ──────────────────────────────────────────────────


def extract_text_from_pdf(pdf_path: str) -> list:
    """Read PDF page by page. Returns list of {page_no, text}"""
    print(f"📄 Reading PDF: {pdf_path}")
    pages = []

    try:
        md_pages = pymupdf4llm.to_markdown(pdf_path, page_chunks=True)
        for i, page in enumerate(md_pages):
            text = page.get("text", "").strip()
            if text:
                pages.append({
                    "page_no": i + 1,
                    "text": text
                })
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        raise

    print(f"✅ Extracted {len(pages)} pages with text")
    return pages


def split_into_chunks(pages: list) -> list:
    """Split pages into overlapping chunks of ~500 words"""
    chunks = []
    chunk_id = 0

    for page in pages:
        words = page["text"].split()
        page_no = page["page_no"]

        start = 0
        while start < len(words):
            end = start + CHUNK_SIZE
            chunk_text = " ".join(words[start:end])

            chunks.append({
                "chunk_id": chunk_id,
                "page_no": page_no,
                "text": chunk_text,
                "section_label": detect_section(chunk_text[:100])
            })

            chunk_id += 1
            start += CHUNK_SIZE - CHUNK_OVERLAP

    print(f"✅ Created {len(chunks)} chunks total")
    return chunks


def detect_section(text: str) -> str:
    """Detect which financial section this chunk belongs to"""
    t = text.lower()
    if any(k in t for k in ["revenue", "net income", "earnings", "gross profit"]):
        return "Income Statement"
    elif any(k in t for k in ["cash flow", "operating activities", "capital expenditure"]):
        return "Cash Flow"
    elif any(k in t for k in ["total assets", "liabilities", "balance sheet", "equity"]):
        return "Balance Sheet"
    elif any(k in t for k in ["notes to", "note 1", "note 2", "footnote"]):
        return "Notes"
    else:
        return "Body"


def save_chunks(chunks: list, session_id: str):
    """Save chunks to disk so we don't re-process every time"""
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, f"{session_id}_chunks.pkl")
    with open(path, "wb") as f:
        pickle.dump(chunks, f)
    print(f"💾 Saved → {path}")


def load_chunks(session_id: str) -> list:
    """Load previously saved chunks"""
    path = os.path.join(DATA_DIR, f"{session_id}_chunks.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No chunks found for session: {session_id}")
    with open(path, "rb") as f:
        return pickle.load(f)


def ingest_pdf(pdf_path: str, session_id: str) -> list:
    """MAIN FUNCTION: extract → split → save → return chunks"""
    pages = extract_text_from_pdf(pdf_path)
    chunks = split_into_chunks(pages)
    save_chunks(chunks, session_id)
    return chunks