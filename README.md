# 💹 FinTrustRAG

### A Numerical Consistency Trust Scoring Framework for Hallucination Detection in Financial RAG

[![Python](https://img.shields.io/badge/Python-3.13-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-blue)](https://reactjs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📌 Project Overview

FinTrustRAG is a financial document question-answering system that addresses a critical and previously unsolved problem: **numerical hallucination in financial RAG systems**.

When users ask questions about financial documents (SEC filings, annual reports), Large Language Models (LLMs) often generate answers with **mathematically incorrect numbers** — even when the correct figures are present in the retrieved document. This is dangerous in financial contexts where wrong numbers can influence real investment decisions.

FinTrustRAG solves this by introducing the **Numerical Consistency Trust Scorer (NCTS)** — a deterministic post-generation verification module that:

- Extracts all numbers from the generated answer
- Verifies each number against source document chunks
- Re-derives financial formulas (profit margin, free cash flow, ROE)
- Produces a **trust score T ∈ [0.00, 1.00]** for every answer

---

## 🏗️ System Architecture

```
User
 │
 ▼
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│  [Upload Panel] [Question Panel] [Result Panel]         │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTP
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Backend                        │
│                                                         │
│  Layer 1: Document Ingestion (PyMuPDF4LLM)             │
│       ↓ PDF → Pages → Chunks → FAISS Index             │
│                                                         │
│  Layer 2: Hybrid Retrieval Engine                       │
│       ↓ FAISS (dense) + BM25 (sparse) + RRF fusion     │
│                                                         │
│  Layer 3: LLM Answer Generation                        │
│       ↓ Groq API (Llama-3.1-8B)                       │
│                                                         │
│  Layer 4: NCTS Verification ⭐ (Core Innovation)       │
│       ↓ Number Extraction → Grounding → Math Check     │
│                                                         │
│  Layer 5: Response Formatter                           │
│       ↓ Answer + Trust Score + Confidence Label        │
└─────────────────────────────────────────────────────────┘
```

---

## ⭐ Core Innovation: NCTS

The **Numerical Consistency Trust Scorer** runs 4 deterministic steps:

```
Step A: Number Extractor
        → Regex extracts all numbers from generated answer
        → Normalises: "$29.9 billion" → 29900000000.0

Step B: Grounding Checker
        → Checks each number against retrieved source chunks
        → Exact match + fuzzy tolerance matching (ε = 0.1)
        → Computes Grounding Score G ∈ [0, 1]

Step C: Mathematical Consistency Verifier
        → Detects financial metrics (profit margin, FCF, ROE, EPS)
        → Re-derives expected value from source figures
        → Computes Math Score M ∈ [0, 1]

Step D: Score Aggregation
        → T = 0.6 × G + 0.4 × M
        → T ≥ 0.80 → HIGH CONFIDENCE (green)
        → 0.50 ≤ T < 0.80 → MEDIUM CONFIDENCE (amber)
        → T < 0.50 → LOW CONFIDENCE (red) ⚠️
```

---

## 📊 Performance Results

Evaluated on **FinanceBench** (150 expert-annotated financial QA pairs):

| Method                 | Precision | Recall   | F1       | Detection Rate |
| ---------------------- | --------- | -------- | -------- | -------------- |
| Naive RAG              | 0.51      | 0.48     | 0.49     | 43%            |
| RAGAS Faithfulness     | 0.63      | 0.59     | 0.61     | 58%            |
| **FinTrustRAG (Ours)** | **0.87**  | **0.82** | **0.84** | **84%**        |

---

## 🛠️ Tech Stack

| Component        | Technology                      |
| ---------------- | ------------------------------- |
| Backend          | Python 3.13, FastAPI            |
| Frontend         | React 18, JavaScript            |
| PDF Processing   | PyMuPDF4LLM                     |
| Vector Search    | FAISS (dense retrieval)         |
| Keyword Search   | BM25 (sparse retrieval)         |
| Retrieval Fusion | Reciprocal Rank Fusion (RRF)    |
| Embeddings       | all-MiniLM-L6-v2 (384-dim)      |
| LLM              | Groq API (Llama-3.1-8B-Instant) |
| Trust Scoring    | NCTS (custom, no ML inference)  |

---

## 📁 Project Structure

```
FinTrustRAG/
│
├── backend/                    # FastAPI Python backend
│   ├── main.py                 # API routes and server
│   ├── ingestion.py            # PDF processing and chunking
│   ├── retrieval.py            # FAISS + BM25 + RRF retrieval
│   ├── generation.py           # Groq LLM answer generation
│   ├── ncts.py                 # ⭐ Trust scoring module
│   ├── models.py               # Pydantic data models
│   ├── requirements.txt        # Python dependencies
│   └── data/                   # Uploaded PDFs and indexes
│
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── App.js              # Main application
│   │   └── components/         # UI components
│   └── package.json
│
├── .gitignore
└── README.md
```

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- Groq API key (free at console.groq.com)

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/Nakshathra-2808/FinTrustRAG.git
cd FinTrustRAG

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Set up environment variables
# Create backend/.env file and add:
# GROQ_API_KEY=your_key_here

# Start backend server
python main.py
```

Backend runs at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

### Frontend Setup

```bash
# In a new terminal
cd frontend
npm install
npm start
```

Frontend runs at: `http://localhost:3000`

---

## 📖 How to Use

1. **Upload** a financial PDF (SEC 10-K filing, annual report)
2. **Ask** a financial question in natural language
3. **Get** an answer with a trust score
4. **Check** the confidence label:
   - 🟢 HIGH CONFIDENCE (T ≥ 0.80) → Safe to use
   - 🟡 MEDIUM CONFIDENCE (0.50 ≤ T < 0.80) → Quick check recommended
   - 🔴 LOW CONFIDENCE (T < 0.50) → Manual verification required

---

## 💡 Example Questions to Ask

```
Simple Extraction:
→ "What was Apple's total revenue in FY2025?"
→ "What was the net income for 2025?"
→ "How many employees does Apple have?"

Calculation:
→ "What was the gross profit margin in FY2025?"
→ "What was the free cash flow in 2025?"
→ "What was the operating income?"

Comparative:
→ "Did revenue increase from 2024 to 2025?"
→ "Which segment had the highest revenue?"
```

---

## 📚 Dataset

- **FinanceBench** — 150 expert-annotated QA pairs from SEC filings
- Source: [PatronusAI/financebench](https://huggingface.co/datasets/PatronusAI/financebench)
- Documents: SEC EDGAR public filings (apple.com/investor-relations)

---

## 🔬 Research Paper

This project is accompanied by an IEEE-format research paper:

**"FinTrustRAG: A Numerical Consistency Trust Scoring Framework for Hallucination Detection in Financial Retrieval-Augmented Generation"**

Key findings:

- 84% hallucination detection rate vs 43% for naive RAG
- NCTS adds only 0.23 seconds overhead per query
- Runs entirely on CPU — no GPU required
- Precision of 0.87 ensures low false positive rate

---

## 👩‍💻 Author

**Nakshathra**
Department of Computer Science and Engineering
Final Year Project — 2025

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgements

- [PatronusAI](https://github.com/patronusai) for the FinanceBench dataset
- [SEC EDGAR](https://www.sec.gov/edgar) for free access to financial filings
- [Groq](https://groq.com) for free LLM API access
