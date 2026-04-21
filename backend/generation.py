# generation.py
# ONE JOB: Take retrieved chunks + question → send to Groq LLM → return answer
#
# This is where the AI actually "reads" the chunks and forms a human answer.
# Without this, we only have raw text fragments — not answers.

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ── SETTINGS ──────────────────────────────────────────────────────────────────
MODEL = "llama-3.1-8b-instant"   # Free Groq model, fast and capable
MAX_TOKENS = 512                  # Keep answers concise
TEMPERATURE = 0.1                 # Low = more factual, less creative
# ──────────────────────────────────────────────────────────────────────────────

# Initialize Groq client once (not on every request)
_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
        _client = Groq(api_key=api_key)
    return _client


def build_prompt(question: str, chunks: list) -> str:
    """
    Builds the prompt we send to the LLM.

    Structure:
    - System message: tells the model its role
    - Context: the 5 retrieved chunks
    - Question: what the user asked

    WHY THIS STRUCTURE:
    LLMs perform best when given explicit context + instructions.
    We tell it to ONLY use the provided context — this reduces hallucination.
    """

    # Format the chunks into readable context
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(
            f"[Source {i} — Page {chunk['page_no']}, {chunk['section_label']}]\n"
            f"{chunk['text']}\n"
        )
    context = "\n".join(context_parts)

    system_prompt = """You are a financial analyst assistant specializing in SEC filings and annual reports.

RULES:
1. Answer ONLY based on the provided document excerpts below.
2. If the answer is not in the excerpts, say: "This information is not available in the provided document sections."
3. When citing numbers, always mention the source page.
4. Be concise and precise. Financial figures must be exact.
5. Do NOT make up or estimate any numbers."""

    user_prompt = f"""DOCUMENT EXCERPTS:
{context}

QUESTION: {question}

Provide a clear, accurate answer based strictly on the document excerpts above."""

    return system_prompt, user_prompt


def generate_answer(question: str, chunks: list) -> dict:
    """
    MAIN FUNCTION called by main.py for every /ask request.

    Takes the question and top-5 retrieved chunks.
    Sends them to Groq LLM.
    Returns the answer + which chunks were used.

    Returns:
        {
            "answer": "Apple's total revenue in FY2025 was $416,161 million...",
            "model_used": "llama-3.1-8b-instant",
            "chunks_used": 5,
            "source_pages": [39, 25, 40]
        }
    """
    print(f"🤖 Generating answer for: '{question[:60]}'")

    client = get_client()
    system_prompt, user_prompt = build_prompt(question, chunks)

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt}
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )

        answer = response.choices[0].message.content.strip()
        source_pages = list(set(c["page_no"] for c in chunks))

        print(f"✅ Answer generated ({len(answer)} chars)")
        print(f"   Source pages: {source_pages}")

        return {
            "answer": answer,
            "model_used": MODEL,
            "chunks_used": len(chunks),
            "source_pages": source_pages
        }

    except Exception as e:
        print(f"❌ Groq API error: {e}")
        raise RuntimeError(f"LLM generation failed: {str(e)}")
