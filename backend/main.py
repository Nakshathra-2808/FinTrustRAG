
# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import uuid
import os

app = FastAPI(
    title="FinTrustRAG API",
    description="Financial document QA with hallucination detection",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QuestionRequest(BaseModel):
    question: str
    session_id: str


@app.get("/health")
def health_check():
    return {"status": "FinTrustRAG backend is running ✅"}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files accepted")

    session_id = str(uuid.uuid4())[:8]
    os.makedirs("data", exist_ok=True)
    save_path = f"data/{session_id}_{file.filename}"

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    print(f"📁 Saved PDF to {save_path}")

    from ingestion import ingest_pdf
    chunks = ingest_pdf(save_path, session_id)

    return {
        "message": "PDF uploaded and processed ✅",
        "session_id": session_id,
        "filename": file.filename,
        "file_size_kb": round(len(content) / 1024, 1),
        "chunks_created": len(chunks)
    }


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    return {
        "answer": f"[Skeleton] You asked: '{request.question}'. Real answer coming Day 5!",
        "ncts": {
            "grounding_score": 0.0,
            "math_score": 0.0,
            "trust_score": 0.0,
            "confidence_label": "PENDING",
            "flagged_numbers": []
        },
        "source_chunks": [],
        "session_id": request.session_id
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)