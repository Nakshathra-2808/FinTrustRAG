from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import uuid
import os

app = FastAPI(title="FinTrustRAG API", version="1.0.0")

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

    print(f"📁 Saved PDF: {save_path}")

    try:
        from ingestion import ingest_pdf
        chunks = ingest_pdf(save_path, session_id)
        return {
            "message": "PDF uploaded and processed ✅",
            "session_id": session_id,
            "filename": file.filename,
            "file_size_kb": round(len(content) / 1024, 1),
            "chunks_created": len(chunks)
        }
    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
async def ask_question(request: QuestionRequest):
    try:
        from ingestion import load_chunks
        from retrieval import retrieve
        from generation import generate_answer
        from ncts import run_ncts

        # Step 1: Load chunks
        chunks = load_chunks(request.session_id)

        # Step 2: Retrieve top 5 relevant chunks
        top_chunks = retrieve(request.question, request.session_id, chunks)

        # Step 3: Generate answer using LLM
        # NOTE: LLM receives FULL chunk text — no truncation here
        answer = generate_answer(request.question, top_chunks)

        # Step 4: Run NCTS on full chunks
        ncts_result = run_ncts(answer, top_chunks)

        # Step 5: Truncate only for display in source_chunks response
        source_chunks = [
            {
                "chunk_id": c["chunk_id"],
                "page_no": c["page_no"],
                "section_label": c["section_label"],
                "text": c["text"][:800] + "..."  # display only, LLM got full text
            }
            for c in top_chunks
        ]

        return {
            "answer": answer,
            "model_used": "llama-3.1-8b-instant",
            "ncts": ncts_result,
            "source_chunks": source_chunks,
            "session_id": request.session_id
        }

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Session not found. Upload PDF first."
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)