
import { useState, useRef, useEffect } from "react";

const API = "http://127.0.0.1:8000";

// ── 150 QUESTIONS IN 7 CATEGORIES ────────────────────────
const QUESTION_CATEGORIES = [
  {
    id: "income", label: "Income Statement", icon: "📊",
    color: "#1a73e8", bg: "#e8f0fe",
    questions: [
      "What was the total revenue?",
      "What was the net income?",
      "What was the gross profit?",
      "What was the gross profit margin?",
      "What was the operating income?",
      "What was the operating margin?",
      "What was the net profit margin?",
      "What was the cost of revenue?",
      "What was the cost of goods sold?",
      "What was the research and development expenses?",
      "What was the selling general and administrative expenses?",
      "What was the operating expenses?",
      "What was the income before tax?",
      "What was the income tax expense?",
      "What was the effective tax rate?",
      "What was the interest expense?",
      "What was the interest income?",
      "What was the EBITDA?",
      "What was the depreciation and amortization?",
      "What was the net revenue growth rate?",
      "What was the product revenue?",
      "What was the services revenue?",
      "What was the international revenue?",
      "What was the domestic revenue?",
      "What was the other income or expense?",
    ],
  },
  {
    id: "cashflow", label: "Cash Flow", icon: "💰",
    color: "#1e8e3e", bg: "#e6f4ea",
    questions: [
      "What was the operating cash flow?",
      "What was the free cash flow?",
      "What was the capital expenditure?",
      "What was the investing cash flow?",
      "What was the financing cash flow?",
      "What was the net change in cash?",
      "What was the cash paid for income taxes?",
      "What was the cash paid for interest?",
      "What were the stock based compensation expenses?",
      "What was the depreciation in the cash flow statement?",
      "What were the purchases of property plant and equipment?",
      "What were the proceeds from sale of investments?",
      "What were the purchases of investments?",
      "What were the repurchases of common stock?",
      "What were the dividends paid?",
      "What were the proceeds from issuance of debt?",
      "What were the repayments of debt?",
      "What was the net cash from acquisitions?",
      "What was the cash conversion cycle?",
      "What was the capital expenditure as a percentage of revenue?",
      "What was the free cash flow margin?",
      "What were the proceeds from stock option exercises?",
      "What was the cash used in investing activities?",
      "What was the cash used in financing activities?",
      "What was the ending cash and cash equivalents balance?",
    ],
  },
  {
    id: "balance", label: "Balance Sheet", icon: "🏦",
    color: "#7b2d8b", bg: "#f3e8ff",
    questions: [
      "What was the total assets?",
      "What was the total liabilities?",
      "What was the shareholders equity?",
      "What was the total current assets?",
      "What was the total current liabilities?",
      "What was the cash and cash equivalents?",
      "What was the total debt?",
      "What was the long term debt?",
      "What was the short term debt?",
      "What was the accounts receivable?",
      "What was the inventory?",
      "What was the total equity?",
      "What was the retained earnings?",
      "What was the goodwill?",
      "What was the intangible assets?",
      "What was the property plant and equipment net?",
      "What was the deferred revenue?",
      "What was the accounts payable?",
      "What was the accrued liabilities?",
      "What was the working capital?",
      "What was the book value per share?",
      "What was the net debt?",
      "What was the total non current assets?",
      "What was the total non current liabilities?",
      "What was the other long term assets?",
    ],
  },
  {
    id: "ratios", label: "Financial Ratios", icon: "📐",
    color: "#e37400", bg: "#fef3e2",
    questions: [
      "What was the current ratio?",
      "What was the quick ratio?",
      "What was the debt to equity ratio?",
      "What was the return on equity?",
      "What was the return on assets?",
      "What was the return on invested capital?",
      "What was the earnings per share?",
      "What was the diluted earnings per share?",
      "What was the price to earnings ratio?",
      "What was the asset turnover ratio?",
      "What was the inventory turnover ratio?",
      "What was the receivables turnover ratio?",
      "What was the debt to assets ratio?",
      "What was the interest coverage ratio?",
      "What was the dividend payout ratio?",
      "What was the operating leverage ratio?",
      "What was the gross margin percentage?",
      "What was the net margin percentage?",
      "What was the EBITDA margin?",
      "What was the return on capital employed?",
      "What was the days sales outstanding?",
      "What was the days payable outstanding?",
      "What was the days inventory outstanding?",
      "What was the cash ratio?",
      "What was the equity multiplier?",
    ],
  },
  {
    id: "pershare", label: "Per Share & Equity", icon: "📈",
    color: "#d93025", bg: "#fce8e6",
    questions: [
      "What was the basic earnings per share?",
      "What was the diluted shares outstanding?",
      "What was the basic shares outstanding?",
      "What were the dividends per share?",
      "What was the revenue per share?",
      "What was the free cash flow per share?",
      "What was the book value per share?",
      "What was the net asset value per share?",
      "How many shares were repurchased?",
      "What was the total value of share repurchases?",
      "What was the weighted average diluted shares?",
      "What was the stock based compensation per share?",
      "How many shares were outstanding at year end?",
      "What was the change in shares outstanding?",
      "What was the total equity per share?",
    ],
  },
  {
    id: "growth", label: "YoY & Growth", icon: "📉",
    color: "#0d7377", bg: "#e0f7f7",
    questions: [
      "How did total revenue change year over year?",
      "How did net income change year over year?",
      "How did gross profit change year over year?",
      "How did operating income change year over year?",
      "How did earnings per share change year over year?",
      "How did operating cash flow change year over year?",
      "How did total assets change year over year?",
      "How did total debt change year over year?",
      "How did research and development expenses change year over year?",
      "How did capital expenditure change year over year?",
      "What was the revenue growth rate?",
      "What was the net income growth rate?",
      "What was the operating income growth rate?",
      "What was the free cash flow growth rate?",
      "What was the gross profit growth rate?",
    ],
  },
  {
    id: "business", label: "Business & Operations", icon: "🏢",
    color: "#5f6368", bg: "#f1f3f4",
    questions: [
      "What were the main sources of revenue?",
      "What were the primary business segments?",
      "What was the revenue breakdown by segment?",
      "What was the operating income by segment?",
      "What were the major risk factors disclosed?",
      "What acquisitions were made during the year?",
      "What was the total acquisition cost?",
      "How many employees did the company have?",
      "What were the significant accounting policies?",
      "What were the contingent liabilities?",
      "What was the total lease obligations?",
      "What were the future minimum lease payments?",
      "What were the commitments and contingencies?",
      "What was the geographic revenue breakdown?",
      "What were the related party transactions?",
      "What was the total pension obligation?",
      "What were the off balance sheet arrangements?",
      "What were the subsequent events disclosed?",
      "What was the audit opinion issued?",
      "What were the material weaknesses reported?",
    ],
  },
];

const INITIAL_SHOW = 5;
const TOTAL_Q = QUESTION_CATEGORIES.reduce((s, c) => s + c.questions.length, 0);

// ── STYLES ───────────────────────────────────────────────
const styles = `
  @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
  :root{
    --white:#ffffff;--off-white:#f8faff;--surface2:#f1f5ff;--surface3:#e8eeff;
    --border:#dde3f0;--border2:#c5cee8;
    --text:#0d1b3e;--text2:#3d4f7c;--text3:#6b7ba8;--text4:#9aa3c2;
    --blue:#1a73e8;--blue2:#1557b0;--blue3:#4285f4;
    --blue-light:#e8f0fe;--blue-mid:#c2d4fc;
    --black:#0d1b3e;--black2:#1a2744;
    --green:#1e8e3e;--green-bg:#e6f4ea;
    --amber:#e37400;--amber-bg:#fef3e2;
    --red:#d93025;--red-bg:#fce8e6;
    --shadow-sm:0 1px 3px rgba(13,27,62,0.08);
    --shadow:0 4px 16px rgba(13,27,62,0.10),0 1px 4px rgba(13,27,62,0.06);
    --shadow-lg:0 8px 32px rgba(13,27,62,0.12),0 2px 8px rgba(13,27,62,0.08);
    --shadow-blue:0 4px 20px rgba(26,115,232,0.18);
    --radius:12px;--radius-sm:8px;--radius-lg:16px;
  }
  html{scroll-behavior:smooth}
  body{background:var(--off-white);color:var(--text);font-family:'Plus Jakarta Sans',sans-serif;min-height:100vh;overflow-x:hidden;-webkit-font-smoothing:antialiased}
  .bg-layer{position:fixed;inset:0;z-index:0;pointer-events:none;background:radial-gradient(ellipse 80% 50% at 10% 0%,rgba(26,115,232,0.07) 0%,transparent 60%),radial-gradient(ellipse 60% 40% at 90% 100%,rgba(66,133,244,0.05) 0%,transparent 55%)}
  .bg-dots{position:fixed;inset:0;z-index:0;pointer-events:none;background-image:radial-gradient(circle,rgba(26,115,232,0.12) 1px,transparent 1px);background-size:32px 32px;opacity:0.5}
  .app{position:relative;z-index:1;max-width:920px;margin:0 auto;padding:0 20px 100px}

  /* HEADER */
  .header{display:flex;align-items:center;justify-content:space-between;padding:28px 0 32px;border-bottom:1.5px solid var(--border);margin-bottom:40px;animation:slideDown 0.5s cubic-bezier(0.16,1,0.3,1) both}
  @keyframes slideDown{from{opacity:0;transform:translateY(-16px)}to{opacity:1;transform:translateY(0)}}
  .logo{display:flex;align-items:center;gap:14px}
  .logo-icon{width:40px;height:40px;border-radius:10px;background:var(--blue);display:flex;align-items:center;justify-content:center;box-shadow:var(--shadow-blue);flex-shrink:0}
  .logo-icon svg{width:22px;height:22px;fill:white}
  .logo-name{font-size:20px;font-weight:700;color:var(--text);letter-spacing:-0.4px;line-height:1}
  .logo-name span{color:var(--blue)}
  .logo-sub{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:500;color:var(--text3);letter-spacing:0.08em;text-transform:uppercase}
  .status-chip{display:flex;align-items:center;gap:7px;padding:6px 14px;background:var(--white);border:1.5px solid var(--border);border-radius:20px;font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:500;color:var(--text3);box-shadow:var(--shadow-sm);transition:all 0.3s}
  .status-chip.active{border-color:var(--blue-mid);color:var(--blue);background:var(--blue-light)}
  .status-dot{width:7px;height:7px;border-radius:50%;background:var(--border2);transition:background 0.3s}
  .status-chip.active .status-dot{background:var(--blue);box-shadow:0 0 0 3px rgba(26,115,232,0.2);animation:livePulse 2s infinite}
  @keyframes livePulse{0%,100%{box-shadow:0 0 0 3px rgba(26,115,232,0.2)}50%{box-shadow:0 0 0 5px rgba(26,115,232,0.08)}}

  /* STEP */
  .step-label{display:flex;align-items:center;gap:10px;margin-bottom:14px;animation:fadeIn 0.4s ease both}
  .step-num{width:24px;height:24px;border-radius:50%;background:var(--blue);color:white;font-size:11px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0}
  .step-text{font-size:12px;font-weight:600;color:var(--text3);letter-spacing:0.06em;text-transform:uppercase}
  @keyframes fadeIn{from{opacity:0}to{opacity:1}}
  @keyframes fadeUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}

  /* CARD */
  .card{background:var(--white);border:1.5px solid var(--border);border-radius:var(--radius-lg);box-shadow:var(--shadow);overflow:hidden;transition:box-shadow 0.2s}
  .card:hover{box-shadow:var(--shadow-lg)}
  .card-body{padding:24px}

  /* UPLOAD */
  .upload-card{margin-bottom:28px;animation:fadeUp 0.5s cubic-bezier(0.16,1,0.3,1) 0.1s both}
  .upload-zone{border:2px dashed var(--border2);border-radius:var(--radius);padding:40px 24px;text-align:center;cursor:pointer;transition:all 0.25s cubic-bezier(0.16,1,0.3,1);background:var(--surface2);position:relative;overflow:hidden}
  .upload-zone:hover,.upload-zone.drag{border-color:var(--blue);background:var(--blue-light);transform:translateY(-2px);box-shadow:var(--shadow-blue)}
  .upload-icon-wrap{width:64px;height:64px;border-radius:16px;background:var(--white);border:1.5px solid var(--border);display:flex;align-items:center;justify-content:center;margin:0 auto 16px;box-shadow:var(--shadow-sm);transition:all 0.25s}
  .upload-zone:hover .upload-icon-wrap,.upload-zone.drag .upload-icon-wrap{background:var(--blue);border-color:var(--blue);box-shadow:var(--shadow-blue);transform:scale(1.05)}
  .upload-icon-wrap svg{width:28px;height:28px;transition:fill 0.25s}
  .upload-zone:hover .upload-icon-wrap svg,.upload-zone.drag .upload-icon-wrap svg{fill:white}
  .upload-title{font-size:16px;font-weight:600;color:var(--text);margin-bottom:6px}
  .upload-sub{font-family:'JetBrains Mono',monospace;font-size:13px;color:var(--text3)}
  .file-selected-banner{display:flex;align-items:center;gap:12px;background:var(--blue-light);border:1.5px solid var(--blue-mid);border-radius:var(--radius-sm);padding:12px 16px;margin-top:12px}
  .file-sel-icon{width:36px;height:36px;border-radius:8px;background:var(--blue);display:flex;align-items:center;justify-content:center;flex-shrink:0}
  .file-sel-icon svg{width:18px;height:18px;fill:white}
  .file-sel-name{font-size:14px;font-weight:600;color:var(--text);margin-bottom:2px}
  .file-sel-meta{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--text3)}
  .upload-success{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px;background:var(--green-bg);border:1.5px solid rgba(30,142,62,0.25);border-radius:var(--radius);padding:16px 20px;animation:successPop 0.4s cubic-bezier(0.16,1,0.3,1) both}
  @keyframes successPop{from{opacity:0;transform:scale(0.97)}to{opacity:1;transform:scale(1)}}
  .upload-file-info{display:flex;align-items:center;gap:12px}
  .file-icon-green{width:40px;height:40px;border-radius:10px;background:var(--green);display:flex;align-items:center;justify-content:center;flex-shrink:0}
  .file-icon-green svg{width:20px;height:20px;fill:white}
  .file-name{font-size:14px;font-weight:600;color:var(--text);margin-bottom:3px}
  .file-meta{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--green)}
  .session-badge{display:flex;align-items:center;gap:6px;font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:500;background:var(--white);border:1.5px solid rgba(30,142,62,0.3);color:var(--green);padding:6px 12px;border-radius:6px}

  /* BUTTONS */
  .btn-primary{width:100%;margin-top:16px;padding:14px 24px;background:var(--blue);color:white;border:none;border-radius:var(--radius-sm);font-family:'Plus Jakarta Sans',sans-serif;font-size:14px;font-weight:600;cursor:pointer;transition:all 0.2s cubic-bezier(0.16,1,0.3,1);display:flex;align-items:center;justify-content:center;gap:8px;box-shadow:0 2px 8px rgba(26,115,232,0.30)}
  .btn-primary:hover:not(:disabled){background:var(--blue2);transform:translateY(-1px);box-shadow:0 4px 16px rgba(26,115,232,0.38)}
  .btn-primary:disabled{opacity:0.45;cursor:not-allowed;box-shadow:none}
  .btn-analyze{padding:14px 24px;background:var(--blue);color:white;border:none;border-radius:var(--radius-sm);font-family:'Plus Jakarta Sans',sans-serif;font-size:14px;font-weight:600;cursor:pointer;transition:all 0.2s cubic-bezier(0.16,1,0.3,1);white-space:nowrap;display:flex;align-items:center;gap:7px;box-shadow:0 2px 8px rgba(26,115,232,0.25);flex-shrink:0}
  .btn-analyze:hover:not(:disabled){background:var(--blue2);transform:translateY(-1px);box-shadow:0 4px 14px rgba(26,115,232,0.35)}
  .btn-analyze:disabled{opacity:0.4;cursor:not-allowed;transform:none;box-shadow:none}
  .btn-analyze svg{width:15px;height:15px;fill:white}

  /* QUERY */
  .query-card{margin-bottom:28px;animation:fadeUp 0.5s cubic-bezier(0.16,1,0.3,1) 0.2s both}
  .ask-row{display:flex;gap:10px;align-items:flex-end}
  .question-wrap{flex:1}
  .question-input{width:100%;background:var(--surface2);border:1.5px solid var(--border);border-radius:var(--radius-sm);padding:14px 18px;font-family:'Plus Jakarta Sans',sans-serif;font-size:14px;color:var(--text);outline:none;transition:all 0.2s;resize:none;line-height:1.55}
  .question-input:focus{border-color:var(--blue);background:var(--white);box-shadow:0 0 0 3px rgba(26,115,232,0.12)}
  .question-input::placeholder{color:var(--text4)}
  .question-input:disabled{opacity:0.5;cursor:not-allowed}

  /* CATEGORY BROWSER */
  .cat-browser{margin-top:20px;border-top:1.5px solid var(--border);padding-top:20px}
  .cat-browser-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
  .cat-browser-title{font-size:12px;font-weight:700;color:var(--text3);text-transform:uppercase;letter-spacing:0.08em}
  .cat-total-badge{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:600;background:var(--blue-light);color:var(--blue);padding:2px 8px;border-radius:10px}
  .cat-tabs{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
  .cat-tab{display:flex;align-items:center;gap:6px;padding:7px 14px;border-radius:20px;border:1.5px solid var(--border);background:var(--white);font-size:12px;font-weight:600;color:var(--text2);cursor:pointer;transition:all 0.15s;box-shadow:var(--shadow-sm)}
  .cat-tab:hover{transform:translateY(-1px);box-shadow:var(--shadow)}
  .cat-tab.active{border-color:transparent;color:white;box-shadow:0 2px 8px rgba(0,0,0,0.15)}
  .cat-tab-icon{font-size:13px}
  .cat-tab-count{font-family:'JetBrains Mono',monospace;font-size:9px;font-weight:700;background:rgba(255,255,255,0.25);padding:1px 5px;border-radius:8px}
  .cat-tab:not(.active) .cat-tab-count{background:var(--surface3);color:var(--text3)}

  /* QUESTIONS PANEL */
  .q-panel{background:var(--surface2);border:1.5px solid var(--border);border-radius:var(--radius);overflow:hidden;animation:fadeIn 0.2s ease both}
  .q-panel-head{display:flex;align-items:center;gap:10px;padding:12px 16px;border-bottom:1.5px solid var(--border);background:var(--white)}
  .q-panel-icon{font-size:16px}
  .q-panel-name{font-size:13px;font-weight:700;color:var(--text);flex:1}
  .q-panel-total{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--text3)}
  .q-grid{display:grid;grid-template-columns:1fr 1fr;gap:6px;padding:12px}
  .q-pill{font-size:12px;font-weight:500;padding:9px 12px;border-radius:var(--radius-sm);border:1.5px solid var(--border);background:var(--white);color:var(--text2);cursor:pointer;transition:all 0.15s;text-align:left;line-height:1.4;box-shadow:var(--shadow-sm)}
  .q-pill:hover:not(:disabled){transform:translateY(-1px);box-shadow:var(--shadow)}
  .q-pill:disabled{opacity:0.4;cursor:not-allowed}
  .show-more-row{display:flex;align-items:center;justify-content:center;padding:10px 12px;border-top:1.5px solid var(--border);gap:8px}
  .btn-show-more{display:flex;align-items:center;gap:6px;padding:8px 20px;border-radius:20px;border:1.5px solid var(--border);background:var(--white);font-size:12px;font-weight:600;color:var(--text2);cursor:pointer;transition:all 0.15s;box-shadow:var(--shadow-sm)}
  .btn-show-more:hover{border-color:var(--blue);color:var(--blue);background:var(--blue-light);transform:translateY(-1px)}
  .show-more-count{font-family:'JetBrains Mono',monospace;font-size:10px;background:var(--surface3);color:var(--text3);padding:2px 7px;border-radius:8px}

  /* HISTORY */
  .history-strip{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px;padding-top:16px;border-top:1px solid var(--border)}
  .history-pill{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:500;padding:5px 10px;border-radius:4px;border:1px solid var(--border);background:var(--surface2);color:var(--text3);cursor:pointer;max-width:220px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;transition:all 0.15s}
  .history-pill:hover{color:var(--blue);border-color:var(--blue-mid);background:var(--blue-light)}

  /* LOADING */
  .loading-wrap{margin-top:20px;animation:fadeIn 0.3s ease both}
  .loading-bar-track{height:3px;background:var(--border);border-radius:3px;overflow:hidden;margin-bottom:12px}
  .loading-bar-fill{height:100%;border-radius:3px;background:linear-gradient(90deg,var(--blue),var(--blue3),#74b9ff,var(--blue));background-size:300% 100%;animation:loadingSlide 1.6s ease infinite;width:100%}
  @keyframes loadingSlide{0%{background-position:100% 0}100%{background-position:-200% 0}}
  .loading-steps{display:flex;align-items:center;justify-content:center;gap:6px;flex-wrap:wrap}
  .loading-step{display:flex;align-items:center;gap:5px;font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--text4);transition:color 0.3s}
  .loading-step.active{color:var(--blue)}.loading-step.done{color:var(--green)}
  .loading-step-dot{width:6px;height:6px;border-radius:50%;background:currentColor;opacity:0.5}
  .loading-step.active .loading-step-dot{opacity:1;animation:dotPulse 0.8s infinite}
  .loading-step.done .loading-step-dot{opacity:1}
  @keyframes dotPulse{0%,100%{transform:scale(1)}50%{transform:scale(1.5)}}
  .step-sep{font-size:9px;color:var(--border2);margin:0 2px}

  /* ERROR */
  .error-box{background:var(--red-bg);border:1.5px solid rgba(217,48,37,0.25);border-radius:var(--radius-sm);padding:14px 18px;margin-top:18px;font-size:13px;font-weight:500;color:var(--red);display:flex;align-items:center;gap:10px;animation:fadeIn 0.3s ease both}
  .error-box svg{width:16px;height:16px;fill:var(--red);flex-shrink:0}

  /* RESULT */
  .result-card{background:var(--white);border:1.5px solid var(--border);border-radius:var(--radius-lg);box-shadow:var(--shadow-lg);overflow:hidden;margin-top:28px;animation:resultReveal 0.45s cubic-bezier(0.16,1,0.3,1) both}
  @keyframes resultReveal{from{opacity:0;transform:translateY(24px) scale(0.98)}to{opacity:1;transform:translateY(0) scale(1)}}
  .result-header{display:flex;align-items:center;justify-content:space-between;padding:16px 24px;background:linear-gradient(135deg,var(--black) 0%,var(--black2) 100%);border-bottom:1px solid rgba(255,255,255,0.08)}
  .result-header-left{display:flex;align-items:center;gap:12px}
  .result-step-badge{width:28px;height:28px;border-radius:8px;background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.15);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:white}
  .result-title{font-size:13px;font-weight:600;color:white}
  .model-tag{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:500;color:rgba(255,255,255,0.5);background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.12);padding:4px 10px;border-radius:4px}
  .answer-body{padding:28px 24px;border-bottom:1.5px solid var(--border)}
  .answer-text{font-size:16px;font-weight:400;line-height:1.75;color:var(--text);white-space:pre-wrap}

  /* NCTS */
  .ncts-panel{padding:24px;background:var(--off-white);border-bottom:1.5px solid var(--border)}
  .ncts-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}
  .ncts-title-wrap{display:flex;align-items:center;gap:8px}
  .ncts-icon{width:28px;height:28px;border-radius:7px;background:var(--black);display:flex;align-items:center;justify-content:center}
  .ncts-icon svg{width:14px;height:14px;fill:white}
  .ncts-title{font-size:13px;font-weight:700;color:var(--text)}
  .ncts-sub{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--text3);margin-top:1px}
  .trust-badge{display:flex;align-items:center;gap:8px;padding:8px 16px;border-radius:20px;font-size:12px;font-weight:700;letter-spacing:0.04em;text-transform:uppercase}
  .badge-dot{width:8px;height:8px;border-radius:50%;background:currentColor;flex-shrink:0}
  .trust-badge.HIGH{background:var(--green-bg);border:1.5px solid rgba(30,142,62,0.3);color:var(--green)}
  .trust-badge.MEDIUM{background:var(--amber-bg);border:1.5px solid rgba(227,116,0,0.3);color:var(--amber)}
  .trust-badge.LOW{background:var(--red-bg);border:1.5px solid rgba(217,48,37,0.3);color:var(--red)}
  .scores-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:20px}
  .score-item{background:var(--white);border:1.5px solid var(--border);border-radius:var(--radius-sm);padding:16px;box-shadow:var(--shadow-sm);transition:box-shadow 0.2s}
  .score-item:hover{box-shadow:var(--shadow)}
  .score-label{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:500;color:var(--text3);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px}
  .score-number{font-family:'JetBrains Mono',monospace;font-size:28px;font-weight:500;line-height:1;margin-bottom:10px}
  .score-pct{font-size:14px;color:var(--text3);margin-left:1px}
  .score-bar-track{height:4px;background:var(--surface3);border-radius:4px;overflow:hidden}
  .score-bar-fill{height:100%;border-radius:4px;transition:width 0.8s cubic-bezier(0.16,1,0.3,1)}
  .math-checks{margin-bottom:16px}
  .math-section-label{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:500;color:var(--text3);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px}
  .math-check-item{background:var(--white);border:1.5px solid var(--border);border-radius:var(--radius-sm);padding:14px 16px;margin-bottom:8px}
  .math-check-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}
  .math-formula{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:500;color:var(--text2)}
  .check-result{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:700;padding:3px 10px;border-radius:4px;text-transform:uppercase;letter-spacing:0.04em}
  .check-result.PASS{background:var(--green-bg);color:var(--green)}
  .check-result.FAIL{background:var(--red-bg);color:var(--red)}
  .check-result.PARTIAL{background:var(--amber-bg);color:var(--amber)}
  .math-values{display:flex;gap:24px;font-family:'JetBrains Mono',monospace;font-size:12px}
  .math-kv{display:flex;flex-direction:column;gap:2px}
  .math-key{font-size:9px;text-transform:uppercase;letter-spacing:0.1em;color:var(--text4)}
  .math-val{font-size:13px;font-weight:500;color:var(--text)}
  .flagged-section{background:var(--red-bg);border:1.5px solid rgba(217,48,37,0.2);border-radius:var(--radius-sm);padding:12px 16px;margin-bottom:12px}
  .flagged-title{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:600;color:var(--red);text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px}
  .flagged-pills{display:flex;flex-wrap:wrap;gap:6px}
  .flagged-pill{font-family:'JetBrains Mono',monospace;font-size:12px;background:var(--white);border:1px solid rgba(217,48,37,0.3);color:var(--red);padding:3px 10px;border-radius:4px;font-weight:500}
  .ncts-note{font-family:'JetBrains Mono',monospace;font-size:11px;color:var(--text3);background:var(--white);border:1.5px solid var(--border);border-radius:var(--radius-sm);padding:10px 14px;margin-top:8px;display:flex;align-items:center;gap:8px}

  /* SOURCES */
  .sources-panel{padding:20px 24px}
  .sources-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:14px}
  .sources-title{font-size:13px;font-weight:700;color:var(--text);display:flex;align-items:center;gap:8px}
  .sources-count{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:600;background:var(--blue-light);color:var(--blue);padding:2px 8px;border-radius:10px}
  .source-list{display:flex;flex-direction:column;gap:8px}
  .source-item{background:var(--surface2);border:1.5px solid var(--border);border-radius:var(--radius-sm);overflow:hidden;cursor:pointer;transition:all 0.15s}
  .source-item:hover{border-color:var(--blue);box-shadow:0 2px 8px rgba(26,115,232,0.1)}
  .source-item-header{display:flex;align-items:center;justify-content:space-between;padding:10px 14px}
  .source-meta{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
  .chunk-id{font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:500;color:var(--text3);background:var(--white);border:1px solid var(--border);padding:2px 7px;border-radius:4px}
  .source-section{font-family:'JetBrains Mono',monospace;font-size:11px;font-weight:500;color:var(--blue);background:var(--blue-light);border:1px solid var(--blue-mid);padding:2px 8px;border-radius:4px}
  .page-no{font-family:'JetBrains Mono',monospace;font-size:10px;color:var(--text4)}
  .source-expand{width:20px;height:20px;border-radius:4px;background:var(--white);border:1px solid var(--border);display:flex;align-items:center;justify-content:center;font-size:9px;color:var(--text3);transition:all 0.2s;flex-shrink:0}
  .source-expand.open{background:var(--blue);border-color:var(--blue);color:white;transform:rotate(180deg)}
  .source-text{padding:12px 14px;font-family:'JetBrains Mono',monospace;font-size:11px;line-height:1.7;color:var(--text2);border-top:1.5px solid var(--border);white-space:pre-wrap;word-break:break-word;background:var(--white)}

  @media(max-width:640px){
    .scores-grid{grid-template-columns:1fr 1fr}
    .ask-row{flex-direction:column}
    .btn-analyze{width:100%;justify-content:center}
    .header{flex-direction:column;align-items:flex-start;gap:16px}
    .q-grid{grid-template-columns:1fr}
    .cat-tabs{gap:6px}
  }
`;

// ── ICONS ────────────────────────────────────────────────
const IconShield = () => (
  <svg viewBox="0 0 24 24"><path d="M12 2L4 5v6c0 5.25 3.4 10.15 8 11.5 4.6-1.35 8-6.25 8-11.5V5L12 2z"/></svg>
);
const IconSearch = () => (
  <svg viewBox="0 0 24 24"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>
);
const IconCheck = () => (
  <svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/></svg>
);
const IconVerify = () => (
  <svg viewBox="0 0 24 24"><path d="M23 12l-2.44-2.79.34-3.69-3.61-.82-1.89-3.2L12 3 8.6 1.5 6.71 4.69 3.1 5.5l.34 3.7L1 12l2.44 2.79-.34 3.7 3.61.82L8.6 22.5 12 21l3.4 1.5 1.89-3.19 3.61-.82-.34-3.69L23 12zm-13 5l-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z"/></svg>
);
const IconError = () => (
  <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
);

function getScoreColor(v) {
  return v >= 0.8 ? "var(--green)" : v >= 0.5 ? "var(--amber)" : "var(--red)";
}

// ── SCORE BAR ────────────────────────────────────────────
function ScoreBar({ value, color }) {
  const [w, setW] = useState(0);
  useEffect(() => { const t = setTimeout(() => setW(Math.round(value * 100)), 120); return () => clearTimeout(t); }, [value]);
  return (
    <div className="score-bar-track">
      <div className="score-bar-fill" style={{ width: `${w}%`, background: color }} />
    </div>
  );
}

// ── LOADING ──────────────────────────────────────────────
function LoadingSteps({ active }) {
  const steps = ["Retrieving", "Generating", "Verifying"];
  const [step, setStep] = useState(0);
  useEffect(() => {
    if (!active) { setStep(0); return; }
    const t = setInterval(() => setStep(s => s < 2 ? s + 1 : s), 1400);
    return () => clearInterval(t);
  }, [active]);
  return (
    <div className="loading-wrap">
      <div className="loading-bar-track"><div className="loading-bar-fill" /></div>
      <div className="loading-steps">
        {steps.map((s, i) => (
          <span key={s} style={{ display: "flex", alignItems: "center", gap: 4 }}>
            <span className={`loading-step ${i < step ? "done" : i === step ? "active" : ""}`}>
              <span className="loading-step-dot" />{s}
            </span>
            {i < steps.length - 1 && <span className="step-sep">→</span>}
          </span>
        ))}
      </div>
    </div>
  );
}

// ── CATEGORY PANEL ───────────────────────────────────────
function CategoryPanel({ cat, disabled, onAsk }) {
  const [showAll, setShowAll] = useState(false);
  const visible   = showAll ? cat.questions : cat.questions.slice(0, INITIAL_SHOW);
  const remaining = cat.questions.length - INITIAL_SHOW;

  return (
    <div className="q-panel">
      <div className="q-panel-head">
        <span className="q-panel-icon">{cat.icon}</span>
        <span className="q-panel-name">{cat.label}</span>
        <span className="q-panel-total">{cat.questions.length} questions</span>
      </div>

      <div className="q-grid">
        {visible.map(q => (
          <button
            key={q}
            className="q-pill"
            disabled={disabled}
            onClick={() => onAsk(q)}
            onMouseEnter={e => {
              e.currentTarget.style.borderColor = cat.color;
              e.currentTarget.style.color = cat.color;
              e.currentTarget.style.background = cat.bg;
            }}
            onMouseLeave={e => {
              e.currentTarget.style.borderColor = "";
              e.currentTarget.style.color = "";
              e.currentTarget.style.background = "";
            }}
          >
            {q}
          </button>
        ))}
      </div>

      <div className="show-more-row">
        {!showAll && remaining > 0 ? (
          <button className="btn-show-more" onClick={() => setShowAll(true)}>
            Show more <span className="show-more-count">+{remaining}</span>
          </button>
        ) : showAll ? (
          <button className="btn-show-more" onClick={() => setShowAll(false)}>
            Show less ↑
          </button>
        ) : null}
      </div>
    </div>
  );
}

// ── SOURCE ITEM ──────────────────────────────────────────
function SourceItem({ chunk, index }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="source-item" onClick={() => setOpen(!open)}
      style={{ animationDelay: `${index * 0.06}s`, animation: "fadeIn 0.3s ease both" }}>
      <div className="source-item-header">
        <div className="source-meta">
          <span className="chunk-id">#{chunk.chunk_id}</span>
          <span className="source-section">{chunk.section_label}</span>
          <span className="page-no">Page {chunk.page_no}</span>
        </div>
        <span className={`source-expand ${open ? "open" : ""}`}>▼</span>
      </div>
      {open && <div className="source-text">{chunk.text}</div>}
    </div>
  );
}

// ── MAIN ─────────────────────────────────────────────────
export default function App() {
  const [file, setFile]             = useState(null);
  const [sessionId, setSessionId]   = useState(null);
  const [uploading, setUploading]   = useState(false);
  const [uploadInfo, setUploadInfo] = useState(null);
  const [question, setQuestion]     = useState("");
  const [asking, setAsking]         = useState(false);
  const [result, setResult]         = useState(null);
  const [error, setError]           = useState(null);
  const [history, setHistory]       = useState([]);
  const [drag, setDrag]             = useState(false);
  const [activeTab, setActiveTab]   = useState("income");
  const fileRef   = useRef();
  const resultRef = useRef();

  const handleFile = f => {
    if (!f || !f.name.endsWith(".pdf")) return;
    setFile(f); setResult(null); setError(null); setUploadInfo(null); setSessionId(null);
  };

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true); setError(null);
    const form = new FormData();
    form.append("file", file);
    try {
      const res = await fetch(`${API}/upload`, { method: "POST", body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");
      setSessionId(data.session_id);
      setUploadInfo(data);
    } catch (e) { setError(e.message); }
    finally { setUploading(false); }
  };

  const handleAsk = async q => {
    const qText = q || question;
    if (!qText.trim() || !sessionId) return;
    setAsking(true); setResult(null); setError(null);
    if (q) setQuestion(q);
    try {
      const res = await fetch(`${API}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: qText, session_id: sessionId }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Request failed");
      setResult(data);
      setHistory(h => [qText, ...h.filter(x => x !== qText)].slice(0, 8));
      setQuestion("");
      setTimeout(() => resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 100);
    } catch (e) { setError(e.message); }
    finally { setAsking(false); }
  };

  const ncts     = result?.ncts;
  const conf     = ncts?.confidence_label;
  const activeCat = QUESTION_CATEGORIES.find(c => c.id === activeTab);

  return (
    <>
      <style>{styles}</style>
      <div className="bg-layer" /><div className="bg-dots" />
      <div className="app">

        {/* HEADER */}
        <header className="header">
          <div className="logo">
            <div className="logo-icon"><IconShield /></div>
            <div>
              <div className="logo-name">Fin<span>Trust</span>RAG</div>
              <div className="logo-sub">NCTS Verification Engine</div>
            </div>
          </div>
          <div className={`status-chip ${sessionId ? "active" : ""}`}>
            <div className="status-dot" />
            {sessionId ? `Session · ${sessionId}` : "No document loaded"}
          </div>
        </header>

        {/* STEP 1 — UPLOAD */}
        <div className="upload-card">
          <div className="step-label">
            <div className="step-num">1</div>
            <span className="step-text">Upload Financial Document</span>
          </div>
          <div className="card">
            <div className="card-body">
              {!uploadInfo ? (
                <>
                  <div
                    className={`upload-zone ${drag ? "drag" : ""}`}
                    onDragOver={e => { e.preventDefault(); setDrag(true); }}
                    onDragLeave={() => setDrag(false)}
                    onDrop={e => { e.preventDefault(); setDrag(false); handleFile(e.dataTransfer.files[0]); }}
                    onClick={() => fileRef.current.click()}
                  >
                    <input ref={fileRef} type="file" accept=".pdf"
                      onChange={e => handleFile(e.target.files[0])} style={{ display: "none" }} />
                    <div className="upload-icon-wrap">
                      <svg viewBox="0 0 24 24" fill="#1a73e8" width="28" height="28">
                        <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zM6 20V4h7v5h5v11H6zm5-5l-3-3 1.41-1.41L11 11.17l4.59-4.58L17 8l-6 6z"/>
                      </svg>
                    </div>
                    <div className="upload-title">{file ? file.name : "Drop your 10-K or SEC filing here"}</div>
                    <div className="upload-sub">{file ? `${(file.size/1024).toFixed(0)} KB · PDF ready` : "PDF only · Drag & drop or click to browse"}</div>
                  </div>
                  {file && (
                    <div className="file-selected-banner">
                      <div className="file-sel-icon">
                        <svg viewBox="0 0 24 24" width="18" height="18" fill="white">
                          <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zM6 20V4h7v5h5v11H6z"/>
                        </svg>
                      </div>
                      <div style={{ flex: 1 }}>
                        <div className="file-sel-name">{file.name}</div>
                        <div className="file-sel-meta">{(file.size/1024).toFixed(0)} KB · PDF</div>
                      </div>
                    </div>
                  )}
                  {file && (
                    <button className="btn-primary" onClick={handleUpload} disabled={uploading}>
                      {uploading ? "Processing document…" : (
                        <>
                          <svg viewBox="0 0 24 24" width="16" height="16" fill="white">
                            <path d="M9 16h6v-6h4l-7-7-7 7h4zm-4 2h14v2H5z"/>
                          </svg>
                          Upload & Index Document
                        </>
                      )}
                    </button>
                  )}
                </>
              ) : (
                <div className="upload-success">
                  <div className="upload-file-info">
                    <div className="file-icon-green"><IconCheck /></div>
                    <div>
                      <div className="file-name">{uploadInfo.filename}</div>
                      <div className="file-meta">{uploadInfo.file_size_kb} KB · {uploadInfo.chunks_created} chunks indexed</div>
                    </div>
                  </div>
                  <div className="session-badge">
                    <svg viewBox="0 0 24 24" width="10" height="10" fill="currentColor">
                      <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
                    </svg>
                    {uploadInfo.session_id}
                  </div>
                </div>
              )}
              {uploading && <LoadingSteps active={true} />}
            </div>
          </div>
        </div>

        {/* STEP 2 — QUERY */}
        <div className="query-card">
          <div className="step-label">
            <div className="step-num">2</div>
            <span className="step-text">Ask a Financial Question</span>
          </div>
          <div className="card">
            <div className="card-body">
              <div className="ask-row">
                <div className="question-wrap">
                  <textarea
                    className="question-input" rows={2}
                    placeholder={sessionId ? "Type a question or click any below…" : "Upload a document above to enable queries"}
                    value={question}
                    onChange={e => setQuestion(e.target.value)}
                    disabled={!sessionId || asking}
                    onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleAsk(); } }}
                  />
                </div>
                <button className="btn-analyze" onClick={() => handleAsk()}
                  disabled={!sessionId || !question.trim() || asking}>
                  {asking ? (
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="white" style={{ animation: "spin 0.8s linear infinite" }}>
                      <path d="M12 4V2C6.48 2 2 6.48 2 12h2c0-4.42 3.58-8 8-8z"/>
                    </svg>
                  ) : <IconSearch />}
                  {asking ? "Analyzing" : "Analyze"}
                </button>
              </div>

              {/* ── CATEGORY BROWSER ── */}
              {sessionId && (
                <div className="cat-browser">
                  <div className="cat-browser-header">
                    <span className="cat-browser-title">Browse {TOTAL_Q} SEC Filing Questions</span>
                    <span className="cat-total-badge">{QUESTION_CATEGORIES.length} categories</span>
                  </div>

                  {/* Tab strip */}
                  <div className="cat-tabs">
                    {QUESTION_CATEGORIES.map(cat => (
                      <button
                        key={cat.id}
                        className={`cat-tab ${activeTab === cat.id ? "active" : ""}`}
                        style={activeTab === cat.id ? { background: cat.color } : {}}
                        onClick={() => setActiveTab(cat.id)}
                      >
                        <span className="cat-tab-icon">{cat.icon}</span>
                        {cat.label}
                        <span className="cat-tab-count">{cat.questions.length}</span>
                      </button>
                    ))}
                  </div>

                  {/* Active panel */}
                  {activeCat && (
                    <CategoryPanel
                      key={activeCat.id}
                      cat={activeCat}
                      disabled={asking}
                      onAsk={handleAsk}
                    />
                  )}
                </div>
              )}

              {/* History */}
              {history.length > 0 && (
                <div className="history-strip">
                  {history.map(h => (
                    <button key={h} className="history-pill" title={h} onClick={() => setQuestion(h)}>
                      ↩ {h}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* LOADING */}
        {asking && <div style={{ padding: "0 4px" }}><LoadingSteps active={true} /></div>}

        {/* ERROR */}
        {error && <div className="error-box"><IconError />{error}</div>}

        {/* STEP 3 — RESULT */}
        {result && (
          <div ref={resultRef}>
            <div className="step-label" style={{ marginTop: 12 }}>
              <div className="step-num">3</div>
              <span className="step-text">Answer & Verification</span>
            </div>
            <div className="result-card">
              <div className="result-header">
                <div className="result-header-left">
                  <div className="result-step-badge">A</div>
                  <span className="result-title">Generated Answer</span>
                </div>
                <span className="model-tag">{result.model_used}</span>
              </div>

              <div className="answer-body">
                <div className="answer-text">{result.answer}</div>
              </div>

              {ncts && (
                <div className="ncts-panel">
                  <div className="ncts-header">
                    <div className="ncts-title-wrap">
                      <div className="ncts-icon"><IconVerify /></div>
                      <div>
                        <div className="ncts-title">NCTS Verification</div>
                        <div className="ncts-sub">Numerical Consistency Trust Score</div>
                      </div>
                    </div>
                    <div className={`trust-badge ${conf}`}>
                      <div className="badge-dot" />{conf} CONFIDENCE
                    </div>
                  </div>

                  <div className="scores-grid">
                    {[
                      { label: "Grounding", val: ncts.grounding_score },
                      { label: "Math",      val: ncts.math_score },
                      { label: "Trust",     val: ncts.trust_score },
                    ].map(({ label, val }) => (
                      <div className="score-item" key={label}>
                        <div className="score-label">{label}</div>
                        <div className="score-number" style={{ color: getScoreColor(val) }}>
                          {(val * 100).toFixed(0)}<span className="score-pct">%</span>
                        </div>
                        <ScoreBar value={val} color={getScoreColor(val)} />
                      </div>
                    ))}
                  </div>

                  {ncts.math_checks?.length > 0 && (
                    <div className="math-checks">
                      <div className="math-section-label">Formula Verification</div>
                      {ncts.math_checks.map((mc, i) => (
                        <div className="math-check-item" key={i}>
                          <div className="math-check-header">
                            <span className="math-formula">{mc.formula}</span>
                            <span className={`check-result ${mc.result}`}>{mc.result}</span>
                          </div>
                          <div className="math-values">
                            <div className="math-kv">
                              <span className="math-key">Expected</span>
                              <span className="math-val">{mc.expected}</span>
                            </div>
                            <div className="math-kv">
                              <span className="math-key">Got</span>
                              <span className="math-val">{mc.got}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {ncts.flagged_numbers?.length > 0 && (
                    <div className="flagged-section">
                      <div className="flagged-title">⚠ Ungrounded Numbers</div>
                      <div className="flagged-pills">
                        {ncts.flagged_numbers.map(n => (
                          <span key={n} className="flagged-pill">{n}</span>
                        ))}
                      </div>
                    </div>
                  )}

                  {ncts.note && (
                    <div className="ncts-note">
                      <svg viewBox="0 0 24 24" width="13" height="13" fill="currentColor">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/>
                      </svg>
                      {ncts.note}
                    </div>
                  )}
                </div>
              )}

              {result.source_chunks?.length > 0 && (
                <div className="sources-panel">
                  <div className="sources-header">
                    <span className="sources-title">
                      Source Chunks
                      <span className="sources-count">{result.source_chunks.length} retrieved</span>
                    </span>
                  </div>
                  <div className="source-list">
                    {result.source_chunks.map((c, i) => (
                      <SourceItem key={c.chunk_id} chunk={c} index={i} />
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

      </div>
      <style>{`@keyframes spin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}`}</style>
    </>
  );
}