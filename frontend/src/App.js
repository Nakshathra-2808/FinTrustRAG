import { useState, useRef } from "react";

const API = "http://127.0.0.1:8000";

const styles = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,400&family=Instrument+Serif:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #0a0c0f;
    --surface: #111318;
    --surface2: #181c22;
    --border: #1e2330;
    --border2: #252d3d;
    --text: #e8eaf0;
    --text2: #7a8499;
    --text3: #4a5268;
    --accent: #4fffb0;
    --accent2: #00d4ff;
    --warn: #ffb347;
    --danger: #ff5f6d;
    --high: #4fffb0;
    --medium: #ffb347;
    --low: #ff5f6d;
  }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
  }

  .noise {
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    opacity: 0.03;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  }

  .grid-bg {
    position: fixed; inset: 0; pointer-events: none; z-index: 0;
    background-image:
      linear-gradient(var(--border) 1px, transparent 1px),
      linear-gradient(90deg, var(--border) 1px, transparent 1px);
    background-size: 40px 40px;
    opacity: 0.4;
  }

  .app {
    position: relative; z-index: 1;
    max-width: 1100px;
    margin: 0 auto;
    padding: 0 24px 80px;
  }

  /* HEADER */
  .header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 32px 0 48px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 40px;
  }

  .logo {
    display: flex; align-items: baseline; gap: 10px;
  }

  .logo-word {
    font-family: 'Instrument Serif', serif;
    font-size: 28px;
    letter-spacing: -0.5px;
    color: var(--text);
  }

  .logo-tag {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: var(--accent);
    background: rgba(79,255,176,0.08);
    border: 1px solid rgba(79,255,176,0.2);
    padding: 2px 8px;
    border-radius: 4px;
    letter-spacing: 0.05em;
  }

  .header-status {
    display: flex; align-items: center; gap: 8px;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    color: var(--text3);
  }

  .status-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 8px var(--accent);
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }

  /* UPLOAD SECTION */
  .section-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.15em;
    color: var(--text3);
    text-transform: uppercase;
    margin-bottom: 12px;
  }

  .upload-zone {
    border: 1.5px dashed var(--border2);
    border-radius: 12px;
    padding: 36px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
    background: var(--surface);
    position: relative;
    overflow: hidden;
  }

  .upload-zone:hover, .upload-zone.drag {
    border-color: var(--accent);
    background: rgba(79,255,176,0.03);
  }

  .upload-zone input {
    position: absolute; inset: 0; opacity: 0; cursor: pointer; width: 100%; height: 100%;
  }

  .upload-icon {
    font-size: 32px; margin-bottom: 12px; display: block;
  }

  .upload-text {
    font-size: 15px; color: var(--text2); margin-bottom: 4px;
  }

  .upload-sub {
    font-size: 12px; color: var(--text3); font-family: 'DM Mono', monospace;
  }

  .upload-success {
    display: flex; align-items: center; justify-content: space-between;
    background: rgba(79,255,176,0.06);
    border: 1px solid rgba(79,255,176,0.2);
    border-radius: 10px;
    padding: 16px 20px;
  }

  .upload-file-info { display: flex; align-items: center; gap: 12px; }

  .file-icon {
    width: 36px; height: 36px; border-radius: 8px;
    background: rgba(79,255,176,0.1);
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
  }

  .file-name {
    font-size: 14px; font-weight: 500; color: var(--text);
    margin-bottom: 2px;
  }

  .file-meta {
    font-family: 'DM Mono', monospace;
    font-size: 11px; color: var(--text3);
  }

  .session-badge {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    background: var(--surface2);
    border: 1px solid var(--border2);
    padding: 6px 12px;
    border-radius: 6px;
    color: var(--accent);
  }

  /* UPLOAD BTN */
  .btn-upload {
    width: 100%; margin-top: 16px;
    padding: 14px;
    background: var(--accent);
    color: #000;
    border: none;
    border-radius: 10px;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    letter-spacing: 0.02em;
  }

  .btn-upload:hover { background: #38ffa0; transform: translateY(-1px); }
  .btn-upload:disabled { opacity: 0.4; cursor: not-allowed; transform: none; }

  /* DIVIDER */
  .divider {
    height: 1px; background: var(--border);
    margin: 36px 0;
  }

  /* ASK SECTION */
  .ask-row {
    display: flex; gap: 12px; align-items: flex-end;
  }

  .question-wrap { flex: 1; }

  .question-input {
    width: 100%;
    background: var(--surface);
    border: 1.5px solid var(--border2);
    border-radius: 10px;
    padding: 14px 18px;
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
    color: var(--text);
    outline: none;
    transition: border-color 0.2s;
    resize: none;
    line-height: 1.5;
  }

  .question-input:focus { border-color: var(--accent); }
  .question-input::placeholder { color: var(--text3); }

  .btn-ask {
    padding: 14px 28px;
    background: transparent;
    color: var(--accent);
    border: 1.5px solid var(--accent);
    border-radius: 10px;
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    white-space: nowrap;
    letter-spacing: 0.05em;
  }

  .btn-ask:hover {
    background: var(--accent); color: #000;
  }

  .btn-ask:disabled { opacity: 0.4; cursor: not-allowed; }

  /* QUICK QUESTIONS */
  .quick-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px; letter-spacing: 0.12em;
    color: var(--text3); text-transform: uppercase;
    margin: 20px 0 10px;
  }

  .quick-pills {
    display: flex; flex-wrap: wrap; gap: 8px;
  }

  .pill {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    padding: 6px 12px;
    border-radius: 20px;
    border: 1px solid var(--border2);
    background: var(--surface);
    color: var(--text2);
    cursor: pointer;
    transition: all 0.15s;
  }

  .pill:hover {
    border-color: var(--accent2);
    color: var(--accent2);
    background: rgba(0,212,255,0.05);
  }

  /* LOADING */
  .loading-bar {
    height: 2px;
    background: linear-gradient(90deg, var(--accent), var(--accent2), var(--accent));
    background-size: 200% 100%;
    border-radius: 2px;
    margin: 24px 0;
    animation: shimmer 1.2s infinite;
  }

  @keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
  }

  .loading-text {
    font-family: 'DM Mono', monospace;
    font-size: 12px; color: var(--text3);
    text-align: center; margin-top: 8px;
    animation: blink 1.2s infinite;
  }

  @keyframes blink {
    0%, 100% { opacity: 1; } 50% { opacity: 0.3; }
  }

  /* RESULT */
  .result-card {
    background: var(--surface);
    border: 1px solid var(--border2);
    border-radius: 14px;
    overflow: hidden;
    margin-top: 28px;
    animation: fadeUp 0.3s ease;
  }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .result-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 24px;
    border-bottom: 1px solid var(--border);
    background: var(--surface2);
  }

  .result-title {
    font-family: 'DM Mono', monospace;
    font-size: 11px; letter-spacing: 0.12em;
    color: var(--text3); text-transform: uppercase;
  }

  .model-tag {
    font-family: 'DM Mono', monospace;
    font-size: 10px; color: var(--text3);
    background: var(--bg);
    border: 1px solid var(--border);
    padding: 3px 8px; border-radius: 4px;
  }

  .answer-body {
    padding: 24px;
  }

  .answer-text {
    font-family: 'Instrument Serif', serif;
    font-size: 18px;
    line-height: 1.7;
    color: var(--text);
    white-space: pre-wrap;
  }

  /* NCTS PANEL */
  .ncts-panel {
    border-top: 1px solid var(--border);
    padding: 20px 24px;
    background: var(--bg);
  }

  .ncts-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 20px;
  }

  .ncts-title {
    font-family: 'DM Mono', monospace;
    font-size: 11px; letter-spacing: 0.15em;
    color: var(--text3); text-transform: uppercase;
  }

  .trust-badge {
    display: flex; align-items: center; gap: 8px;
    padding: 6px 14px;
    border-radius: 20px;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.05em;
  }

  .trust-badge.HIGH {
    background: rgba(79,255,176,0.1);
    border: 1px solid rgba(79,255,176,0.3);
    color: var(--high);
  }

  .trust-badge.MEDIUM {
    background: rgba(255,179,71,0.1);
    border: 1px solid rgba(255,179,71,0.3);
    color: var(--medium);
  }

  .trust-badge.LOW {
    background: rgba(255,95,109,0.1);
    border: 1px solid rgba(255,95,109,0.3);
    color: var(--low);
  }

  .badge-dot {
    width: 6px; height: 6px; border-radius: 50%;
    background: currentColor;
  }

  /* SCORE BARS */
  .scores-grid {
    display: grid; grid-template-columns: 1fr 1fr 1fr;
    gap: 12px; margin-bottom: 20px;
  }

  .score-item {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 16px;
  }

  .score-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px; letter-spacing: 0.1em;
    color: var(--text3); text-transform: uppercase;
    margin-bottom: 8px;
  }

  .score-value {
    font-family: 'DM Mono', monospace;
    font-size: 22px; font-weight: 500;
    margin-bottom: 8px;
  }

  .score-bar-track {
    height: 3px;
    background: var(--border2);
    border-radius: 2px;
    overflow: hidden;
  }

  .score-bar-fill {
    height: 100%; border-radius: 2px;
    transition: width 0.6s ease;
  }

  /* MATH CHECKS */
  .math-checks { margin-bottom: 16px; }

  .math-check-item {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 16px;
    margin-bottom: 8px;
  }

  .math-check-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 10px;
  }

  .math-formula {
    font-family: 'DM Mono', monospace;
    font-size: 11px; color: var(--text2);
  }

  .check-result {
    font-family: 'DM Mono', monospace;
    font-size: 11px; font-weight: 500;
    padding: 3px 10px; border-radius: 4px;
  }

  .check-result.PASS {
    background: rgba(79,255,176,0.1); color: var(--high);
  }
  .check-result.FAIL {
    background: rgba(255,95,109,0.1); color: var(--low);
  }
  .check-result.PARTIAL {
    background: rgba(255,179,71,0.1); color: var(--medium);
  }

  .math-row {
    display: flex; gap: 20px;
    font-family: 'DM Mono', monospace; font-size: 12px;
  }

  .math-field { color: var(--text3); }
  .math-val { color: var(--text); margin-left: 6px; }

  /* FLAGGED */
  .flagged-section { margin-bottom: 16px; }

  .flagged-title {
    font-family: 'DM Mono', monospace;
    font-size: 10px; letter-spacing: 0.1em;
    color: var(--text3); text-transform: uppercase;
    margin-bottom: 8px;
  }

  .flagged-pills { display: flex; flex-wrap: wrap; gap: 6px; }

  .flagged-pill {
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    background: rgba(255,95,109,0.08);
    border: 1px solid rgba(255,95,109,0.25);
    color: var(--low);
    padding: 4px 10px; border-radius: 5px;
  }

  /* SOURCES */
  .sources-panel {
    border-top: 1px solid var(--border);
    padding: 20px 24px;
  }

  .sources-title {
    font-family: 'DM Mono', monospace;
    font-size: 10px; letter-spacing: 0.15em;
    color: var(--text3); text-transform: uppercase;
    margin-bottom: 14px;
  }

  .source-list { display: flex; flex-direction: column; gap: 8px; }

  .source-item {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
    cursor: pointer;
    transition: border-color 0.15s;
  }

  .source-item:hover { border-color: var(--border2); }

  .source-item-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 14px;
  }

  .source-meta {
    display: flex; align-items: center; gap: 10px;
  }

  .chunk-id {
    font-family: 'DM Mono', monospace;
    font-size: 10px; color: var(--text3);
    background: var(--bg);
    border: 1px solid var(--border);
    padding: 2px 7px; border-radius: 4px;
  }

  .source-section {
    font-family: 'DM Mono', monospace;
    font-size: 11px; color: var(--accent2);
    background: rgba(0,212,255,0.06);
    border: 1px solid rgba(0,212,255,0.15);
    padding: 2px 8px; border-radius: 4px;
  }

  .page-no {
    font-family: 'DM Mono', monospace;
    font-size: 10px; color: var(--text3);
  }

  .source-expand {
    font-size: 10px; color: var(--text3);
    transition: transform 0.2s;
  }

  .source-expand.open { transform: rotate(180deg); }

  .source-text {
    padding: 0 14px 12px;
    font-family: 'DM Mono', monospace;
    font-size: 11px; line-height: 1.7;
    color: var(--text2);
    border-top: 1px solid var(--border);
    padding-top: 10px;
    white-space: pre-wrap;
    word-break: break-word;
  }

  /* ERROR */
  .error-box {
    background: rgba(255,95,109,0.06);
    border: 1px solid rgba(255,95,109,0.2);
    border-radius: 10px;
    padding: 16px 20px;
    margin-top: 20px;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    color: var(--low);
  }

  /* HISTORY */
  .history-strip {
    display: flex; gap: 8px;
    flex-wrap: wrap;
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid var(--border);
  }

  .history-pill {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    padding: 4px 10px;
    border-radius: 4px;
    border: 1px solid var(--border2);
    background: var(--surface);
    color: var(--text3);
    cursor: pointer;
    max-width: 220px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    transition: all 0.15s;
  }

  .history-pill:hover {
    color: var(--text2);
    border-color: var(--text3);
  }

  @media (max-width: 640px) {
    .scores-grid { grid-template-columns: 1fr 1fr; }
    .ask-row { flex-direction: column; }
    .btn-ask { width: 100%; }
  }
`;

const QUICK_QUESTIONS = [
  "What was Apple total revenue in 2025?",
  "What was Apple gross profit margin in 2025?",
  "What was Apple free cash flow in 2025?",
  "What was Apple net income in 2025?",
  "What was Apple iPhone revenue in 2025?",
  "What was Apple services revenue in 2025?",
];

function ScoreBar({ value, color }) {
  return (
    <div className="score-bar-track">
      <div
        className="score-bar-fill"
        style={{ width: `${Math.round(value * 100)}%`, background: color }}
      />
    </div>
  );
}

function getScoreColor(val) {
  if (val >= 0.8) return "var(--high)";
  if (val >= 0.5) return "var(--medium)";
  return "var(--low)";
}

function SourceItem({ chunk }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="source-item" onClick={() => setOpen(!open)}>
      <div className="source-item-header">
        <div className="source-meta">
          <span className="chunk-id">#{chunk.chunk_id}</span>
          <span className="source-section">{chunk.section_label}</span>
          <span className="page-no">p.{chunk.page_no}</span>
        </div>
        <span className={`source-expand ${open ? "open" : ""}`}>▼</span>
      </div>
      {open && <div className="source-text">{chunk.text}</div>}
    </div>
  );
}

export default function App() {
  const [file, setFile] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadInfo, setUploadInfo] = useState(null);

  const [question, setQuestion] = useState("");
  const [asking, setAsking] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const [history, setHistory] = useState([]);
  const [drag, setDrag] = useState(false);
  const fileRef = useRef();

  const handleFile = (f) => {
    if (!f || !f.name.endsWith(".pdf")) return;
    setFile(f);
    setResult(null);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError(null);
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await fetch(`${API}/upload`, { method: "POST", body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");
      setSessionId(data.session_id);
      setUploadInfo(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setUploading(false);
    }
  };

  const handleAsk = async (q) => {
    const qText = q || question;
    if (!qText.trim() || !sessionId) return;
    setAsking(true);
    setResult(null);
    setError(null);
    try {
      const res = await fetch(`${API}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: qText, session_id: sessionId }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Request failed");
      setResult(data);
      setHistory((h) => [qText, ...h.filter((x) => x !== qText)].slice(0, 8));
      setQuestion("");
    } catch (e) {
      setError(e.message);
    } finally {
      setAsking(false);
    }
  };

  const ncts = result?.ncts;
  const conf = ncts?.confidence_label;

  return (
    <>
      <style>{styles}</style>
      <div className="noise" />
      <div className="grid-bg" />

      <div className="app">
        {/* HEADER */}
        <header className="header">
          <div className="logo">
            <span className="logo-word">FinTrustRAG</span>
            <span className="logo-tag">NCTS v1.0</span>
          </div>
          <div className="header-status">
            <div className="status-dot" />
            {sessionId
              ? `session · ${sessionId}`
              : "no document loaded"}
          </div>
        </header>

        {/* UPLOAD */}
        <div className="section-label">01 — Document</div>

        {!uploadInfo ? (
          <>
            <div
              className={`upload-zone ${drag ? "drag" : ""}`}
              onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
              onDragLeave={() => setDrag(false)}
              onDrop={(e) => { e.preventDefault(); setDrag(false); handleFile(e.dataTransfer.files[0]); }}
              onClick={() => fileRef.current.click()}
            >
              <input
                ref={fileRef}
                type="file"
                accept=".pdf"
                onChange={(e) => handleFile(e.target.files[0])}
                style={{ display: "none" }}
              />
              <span className="upload-icon">📄</span>
              <div className="upload-text">
                {file ? file.name : "Drop your 10-K or SEC filing here"}
              </div>
              <div className="upload-sub">
                {file
                  ? `${(file.size / 1024).toFixed(0)} KB · PDF`
                  : "PDF only · drag & drop or click"}
              </div>
            </div>

            {file && (
              <button
                className="btn-upload"
                onClick={handleUpload}
                disabled={uploading}
              >
                {uploading ? "Processing document…" : "Upload & Process →"}
              </button>
            )}
          </>
        ) : (
          <div className="upload-success">
            <div className="upload-file-info">
              <div className="file-icon">📄</div>
              <div>
                <div className="file-name">{uploadInfo.filename}</div>
                <div className="file-meta">
                  {uploadInfo.file_size_kb} KB · {uploadInfo.chunks_created} chunks indexed
                </div>
              </div>
            </div>
            <div className="session-badge">sid: {uploadInfo.session_id}</div>
          </div>
        )}

        {uploading && (
          <div style={{ marginTop: 16 }}>
            <div className="loading-bar" />
            <div className="loading-text">chunking · embedding · indexing…</div>
          </div>
        )}

        <div className="divider" />

        {/* ASK */}
        <div className="section-label">02 — Query</div>

        <div className="ask-row">
          <div className="question-wrap">
            <textarea
              className="question-input"
              rows={2}
              placeholder={
                sessionId
                  ? "Ask a financial question about the document…"
                  : "Upload a document first to enable queries"
              }
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              disabled={!sessionId || asking}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleAsk();
                }
              }}
            />
          </div>
          <button
            className="btn-ask"
            onClick={() => handleAsk()}
            disabled={!sessionId || !question.trim() || asking}
          >
            {asking ? "…" : "ANALYZE →"}
          </button>
        </div>

        {sessionId && (
          <>
            <div className="quick-label">Quick queries</div>
            <div className="quick-pills">
              {QUICK_QUESTIONS.map((q) => (
                <button
                  key={q}
                  className="pill"
                  onClick={() => handleAsk(q)}
                  disabled={asking}
                >
                  {q}
                </button>
              ))}
            </div>
          </>
        )}

        {/* HISTORY */}
        {history.length > 0 && (
          <div className="history-strip">
            {history.map((h) => (
              <button
                key={h}
                className="history-pill"
                title={h}
                onClick={() => setQuestion(h)}
              >
                ↩ {h}
              </button>
            ))}
          </div>
        )}

        {/* LOADING */}
        {asking && (
          <div style={{ marginTop: 24 }}>
            <div className="loading-bar" />
            <div className="loading-text">retrieving · generating · verifying…</div>
          </div>
        )}

        {/* ERROR */}
        {error && <div className="error-box">⚠ {error}</div>}

        {/* RESULT */}
        {result && (
          <div className="result-card">
            <div className="result-header">
              <span className="result-title">03 — Answer</span>
              <span className="model-tag">{result.model_used}</span>
            </div>

            <div className="answer-body">
              <div className="answer-text">{result.answer}</div>
            </div>

            {/* NCTS */}
            {ncts && (
              <div className="ncts-panel">
                <div className="ncts-header">
                  <span className="ncts-title">NCTS Verification</span>
                  <div className={`trust-badge ${conf}`}>
                    <div className="badge-dot" />
                    {conf} CONFIDENCE
                  </div>
                </div>

                <div className="scores-grid">
                  {[
                    { label: "Grounding", val: ncts.grounding_score },
                    { label: "Math", val: ncts.math_score },
                    { label: "Trust", val: ncts.trust_score },
                  ].map(({ label, val }) => (
                    <div className="score-item" key={label}>
                      <div className="score-label">{label}</div>
                      <div
                        className="score-value"
                        style={{ color: getScoreColor(val) }}
                      >
                        {(val * 100).toFixed(0)}
                        <span style={{ fontSize: 13, color: "var(--text3)" }}>%</span>
                      </div>
                      <ScoreBar value={val} color={getScoreColor(val)} />
                    </div>
                  ))}
                </div>

                {ncts.math_checks?.length > 0 && (
                  <div className="math-checks">
                    {ncts.math_checks.map((mc, i) => (
                      <div className="math-check-item" key={i}>
                        <div className="math-check-header">
                          <span className="math-formula">{mc.formula}</span>
                          <span className={`check-result ${mc.result}`}>
                            {mc.result}
                          </span>
                        </div>
                        <div className="math-row">
                          <span>
                            <span className="math-field">expected</span>
                            <span className="math-val">{mc.expected}</span>
                          </span>
                          <span>
                            <span className="math-field">got</span>
                            <span className="math-val">{mc.got}</span>
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {ncts.flagged_numbers?.length > 0 && (
                  <div className="flagged-section">
                    <div className="flagged-title">⚠ Flagged Numbers</div>
                    <div className="flagged-pills">
                      {ncts.flagged_numbers.map((n) => (
                        <span key={n} className="flagged-pill">{n}</span>
                      ))}
                    </div>
                  </div>
                )}

                {ncts.note && (
                  <div style={{
                    fontFamily: "'DM Mono', monospace",
                    fontSize: 11,
                    color: "var(--text3)",
                    marginTop: 8,
                    padding: "8px 12px",
                    background: "var(--surface)",
                    borderRadius: 6,
                    border: "1px solid var(--border)"
                  }}>
                    ℹ {ncts.note}
                  </div>
                )}
              </div>
            )}

            {/* SOURCES */}
            {result.source_chunks?.length > 0 && (
              <div className="sources-panel">
                <div className="sources-title">
                  Source Chunks — {result.source_chunks.length} retrieved
                </div>
                <div className="source-list">
                  {result.source_chunks.map((c) => (
                    <SourceItem key={c.chunk_id} chunk={c} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </>
  );
}