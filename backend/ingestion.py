import pymupdf4llm
import os
import pickle
import re

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
DATA_DIR = "data"


def detect_section(text: str) -> str:
    t = text.lower()
    if any(k in t for k in ["cash flow", "operating activities", "investing activities", "financing activities"]):
        return "Cash Flow"
    elif any(k in t for k in ["revenue", "net income", "earnings", "net sales", "gross margin"]):
        return "Income Statement"
    elif any(k in t for k in ["total assets", "liabilities", "balance sheet", "stockholders"]):
        return "Balance Sheet"
    elif any(k in t for k in ["notes to", "note 1", "note 2"]):
        return "Notes"
    return "Body"


def extract_text_from_pdf(pdf_path: str) -> list:
    print(f"📄 Reading PDF: {pdf_path}")
    pages = []
    md_pages = pymupdf4llm.to_markdown(pdf_path, page_chunks=True)
    for i, page in enumerate(md_pages):
        text = page.get("text", "").strip()
        if text:
            pages.append({"page_no": i + 1, "text": text})
    print(f"✅ Extracted {len(pages)} pages")
    return pages


def is_table_line(line: str) -> bool:
    """Detect markdown table rows: |col|col| or |---|---|"""
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|")


def split_page_into_blocks(text: str) -> list:
    """
    Split a page into blocks, keeping markdown tables intact.
    Returns list of (block_text, is_table) tuples.
    
    WHY: Word-count chunking splits tables mid-row, 
    cutting off financial figures. This keeps each table 
    as one atomic block so numbers are never separated 
    from their row headers.
    """
    lines = text.split("\n")
    blocks = []
    current_block = []
    in_table = False

    for line in lines:
        line_is_table = is_table_line(line)

        if line_is_table and not in_table:
            # Flush current prose block
            if current_block:
                blocks.append(("\n".join(current_block), False))
                current_block = []
            in_table = True
            current_block.append(line)

        elif not line_is_table and in_table:
            # Flush current table block
            if current_block:
                blocks.append(("\n".join(current_block), True))
                current_block = []
            in_table = False
            if line.strip():
                current_block.append(line)

        else:
            if line.strip():
                current_block.append(line)

    # Flush whatever remains
    if current_block:
        blocks.append(("\n".join(current_block), in_table))

    return blocks

def split_into_chunks(pages: list) -> list:
    chunks = []
    chunk_id = 0

    for page in pages:
        page_no = page["page_no"]
        blocks = split_page_into_blocks(page["text"])

        current_words = []

        for block_text, is_table in blocks:
            block_words = block_text.split()

            if is_table:
                # Flush any accumulated prose first
                if current_words:
                    flush_text = " ".join(current_words)
                    chunks.append({
                        "chunk_id": chunk_id,
                        "page_no": page_no,
                        "text": flush_text,
                        "section_label": detect_section(flush_text[:200])
                    })
                    chunk_id += 1
                    current_words = []

                # Check if this is a financial statement table
                # If so, merge with next table block (they belong together)
                section = detect_section(block_text[:200])
                if section == "Cash Flow" and chunks and chunks[-1].get("section_label") == "Cash Flow":
                    # Merge with previous Cash Flow chunk instead of creating new one
                    prev = chunks[-1]
                    prev["text"] = prev["text"] + "\n" + block_text
                else:
                    chunks.append({
                        "chunk_id": chunk_id,
                        "page_no": page_no,
                        "text": block_text,
                        "section_label": section
                    })
                    chunk_id += 1

            else:
                current_words.extend(block_words)
                while len(current_words) >= CHUNK_SIZE:
                    chunk_text = " ".join(current_words[:CHUNK_SIZE])
                    chunks.append({
                        "chunk_id": chunk_id,
                        "page_no": page_no,
                        "text": chunk_text,
                        "section_label": detect_section(chunk_text[:200])
                    })
                    chunk_id += 1
                    current_words = current_words[CHUNK_SIZE - CHUNK_OVERLAP:]

        if current_words:
            chunk_text = " ".join(current_words)
            chunks.append({
                "chunk_id": chunk_id,
                "page_no": page_no,
                "text": chunk_text,
                "section_label": detect_section(chunk_text[:200])
            })
            chunk_id += 1

    # Re-number chunk_ids cleanly
    for i, chunk in enumerate(chunks):
        chunk["chunk_id"] = i

    print(f"✅ Created {len(chunks)} chunks")
    return chunks



def save_chunks(chunks: list, session_id: str):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, f"{session_id}_chunks.pkl")
    with open(path, "wb") as f:
        pickle.dump(chunks, f)
    print(f"💾 Saved → {path}")


def load_chunks(session_id: str) -> list:
    path = os.path.join(DATA_DIR, f"{session_id}_chunks.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No chunks for session: {session_id}")
    with open(path, "rb") as f:
        return pickle.load(f)


def ingest_pdf(pdf_path: str, session_id: str) -> list:
    pages = extract_text_from_pdf(pdf_path)
    chunks = split_into_chunks(pages)
    save_chunks(chunks, session_id)
    print("🔨 Building indexes...")
    from retrieval import build_indexes
    build_indexes(chunks, session_id)
    print("✅ All indexes built!")
    return chunks