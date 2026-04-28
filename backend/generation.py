# generation.py
# ONE JOB: Take question + chunks → Call Groq → Return answer string

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a financial document analysis assistant.
Answer the following question using ONLY the information provided in the context passages below.
State all numerical figures EXACTLY as they appear in the source documents.
Do not round, convert or paraphrase numbers.
Give a direct, concise answer.
If the context does not contain enough information, respond with:
'The requested information is not available in the provided document sections.'"""


def generate_answer(question: str, chunks: list) -> str:
    """
    Takes question + top 5 chunks.
    Calls Groq Llama-3.1.
    Returns plain answer string.
    """
    print(f"🤖 Generating answer for: '{question[:50]}'")

    # Build context string from chunks
    context = ""
    for i, chunk in enumerate(chunks):
        if isinstance(chunk, dict):
            page = chunk.get("page_no", "?")
            section = chunk.get("section_label", "Body")
            text = chunk.get("text", "")
        else:
            page = "?"
            section = "Body"
            text = str(chunk)

        context += f"\n[Source {i+1} | Page {page} | {section}]\n{text}\n"

    # Build full prompt
    user_message = f"""Context passages from the financial document:
{context}

Question: {question}

Provide a direct answer using only the above context:"""

    # Call Groq API
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0,
        max_tokens=512
    )

    # Extract just the text answer
    answer = response.choices[0].message.content.strip()
    print(f"✅ Answer generated: {answer[:100]}...")
    return answer