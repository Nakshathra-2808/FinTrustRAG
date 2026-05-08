
"""
batch_eval.py  —  Run all 150 questions and save results to CSV
FinTrustRAG evaluation script

Usage:
  1. Make sure your FastAPI backend is running:  uvicorn main:app --reload
  2. Upload your PDF via the UI and copy the session_id shown there
  3. Paste that session_id into SESSION_ID below
  4. Run:  python batch_eval.py
  5. Results → eval_results.csv  (opens in Excel / Google Sheets)

The script also prints a live summary table as it runs so you can
watch progress without opening the CSV.
"""

import csv
import json
import time
import requests
from datetime import datetime

# ── CONFIG — change these ────────────────────────────────────────────────────
API_BASE   = "http://127.0.0.1:8000"
SESSION_ID = "79722004"   # 8-char ID from the upload step
DELAY_SEC  = 1.2   # seconds between requests (avoids Groq rate limit)
OUTPUT_CSV = "eval_results.csv"
# ─────────────────────────────────────────────────────────────────────────────

# ── All 150 questions — same structure as your frontend ──────────────────────
QUESTION_CATEGORIES = {
    "Income Statement": [
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
    "Cash Flow": [
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
    "Balance Sheet": [
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
    "Financial Ratios": [
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
    "Per Share and Equity": [
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
    "YoY and Growth": [
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
    "Business and Operations": [
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
}

# ── CSV column headers ───────────────────────────────────────────────────────
HEADERS = [
    "question_no",
    "category",
    "question",
    "answer",
    "confidence_label",       # HIGH / MEDIUM / LOW / INSUFFICIENT_CONTEXT
    "grounding_score",        # G
    "math_score",             # M
    "trust_score",            # T
    "formula_detected",       # Yes / No
    "math_result",            # PASS / FAIL / PARTIAL / N/A
    "flagged_numbers",        # comma-separated
    "math_expected",          # expected value from NCTS
    "math_got",               # value in LLM answer
    "num_source_chunks",
    "latency_ms",
    "error",                  # blank if ok, error message if request failed
]


def ask_question(question: str, session_id: str) -> dict:
    """Call the /ask endpoint and return the full response dict."""
    resp = requests.post(
        f"{API_BASE}/ask",
        json={"question": question, "session_id": session_id},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def parse_ncts(ncts: dict) -> dict:
    """Flatten NCTS dict into CSV-friendly fields."""
    if not ncts:
        return {
            "confidence_label": "",
            "grounding_score": "",
            "math_score": "",
            "trust_score": "",
            "formula_detected": "No",
            "math_result": "N/A",
            "flagged_numbers": "",
            "math_expected": "",
            "math_got": "",
        }

    label = ncts.get("confidence_label", "")
    G = ncts.get("grounding_score", "")
    M = ncts.get("math_score", "")
    T = ncts.get("trust_score", "")
    flagged = ", ".join(ncts.get("flagged_numbers", []))
    checks = ncts.get("math_checks", [])

    formula_detected = "Yes" if checks else "No"
    math_result  = checks[0].get("result", "N/A") if checks else "N/A"
    math_expected = checks[0].get("expected", "") if checks else ""
    math_got      = checks[0].get("got", "")      if checks else ""

    return {
        "confidence_label": label,
        "grounding_score": G,
        "math_score": M,
        "trust_score": T,
        "formula_detected": formula_detected,
        "math_result": math_result,
        "flagged_numbers": flagged,
        "math_expected": math_expected,
        "math_got": math_got,
    }


def print_progress_line(q_no, total, category, question,
                         label, T, G, M, latency_ms):
    """Print a compact one-line progress update."""
    q_short = question[:45] + "…" if len(question) > 45 else question
    label_coloured = {
        "HIGH":                "HIGH ",
        "MEDIUM":              "MED  ",
        "LOW":                 "LOW  ",
        "INSUFFICIENT_CONTEXT":"N/A  ",
    }.get(label, "?    ")

    T_str = f"{float(T):.2f}" if T not in ("", None) else " -- "
    G_str = f"{float(G):.2f}" if G not in ("", None) else " -- "
    M_str = f"{float(M):.2f}" if M not in ("", None) else " -- "

    print(
        f"  [{q_no:>3}/{total}]  {label_coloured}  "
        f"T={T_str}  G={G_str}  M={M_str}  "
        f"{latency_ms:>5}ms  {q_short}"
    )


def print_category_summary(category: str, rows: list):
    """Print per-category aggregate stats."""
    valid = [r for r in rows if r["trust_score"] not in ("", None)]
    if not valid:
        return

    avg_T = sum(float(r["trust_score"]) for r in valid) / len(valid)
    avg_G = sum(float(r["grounding_score"]) for r in valid
                if r["grounding_score"] not in ("", None)) / max(len(valid), 1)
    math_verified = sum(1 for r in valid if r["formula_detected"] == "Yes")
    high_count = sum(1 for r in valid if r["confidence_label"] == "HIGH")
    med_count  = sum(1 for r in valid if r["confidence_label"] == "MEDIUM")
    low_count  = sum(1 for r in valid if r["confidence_label"] == "LOW")

    print(f"\n  ── {category} ──")
    print(f"     Avg T={avg_T:.2f}  Avg G={avg_G:.2f}  "
          f"Math-verified: {math_verified}/{len(valid)}")
    print(f"     HIGH={high_count}  MEDIUM={med_count}  LOW={low_count}")


def main():
    print("=" * 70)
    print("  FinTrustRAG — Batch Evaluation (150 questions)")
    print(f"  Session: {SESSION_ID}")
    print(f"  Output:  {OUTPUT_CSV}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    if SESSION_ID == "PASTE_YOUR_SESSION_ID_HERE":
        print("\n  ❌  ERROR: Set SESSION_ID at the top of this file first.\n")
        return

    total_questions = sum(len(qs) for qs in QUESTION_CATEGORIES.values())
    all_rows = []
    q_no = 0

    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=HEADERS)
        writer.writeheader()

        for category, questions in QUESTION_CATEGORIES.items():
            print(f"\n{'─'*70}")
            print(f"  Category: {category}  ({len(questions)} questions)")
            print(f"{'─'*70}")
            category_rows = []

            for question in questions:
                q_no += 1
                row = {h: "" for h in HEADERS}
                row["question_no"] = q_no
                row["category"]    = category
                row["question"]    = question

                t_start = time.perf_counter()
                try:
                    data = ask_question(question, SESSION_ID)
                    latency_ms = int((time.perf_counter() - t_start) * 1000)

                    ncts = data.get("ncts", {})
                    parsed = parse_ncts(ncts)

                    row["answer"]           = data.get("answer", "")
                    row["num_source_chunks"] = len(data.get("source_chunks", []))
                    row["latency_ms"]        = latency_ms
                    row.update(parsed)

                    print_progress_line(
                        q_no, total_questions, category, question,
                        parsed["confidence_label"],
                        parsed["trust_score"],
                        parsed["grounding_score"],
                        parsed["math_score"],
                        latency_ms,
                    )

                except requests.exceptions.RequestException as e:
                    latency_ms = int((time.perf_counter() - t_start) * 1000)
                    row["latency_ms"] = latency_ms
                    row["error"] = str(e)
                    print(f"  [{q_no:>3}/{total_questions}]  ❌  ERROR: {e}")

                except Exception as e:
                    row["error"] = str(e)
                    print(f"  [{q_no:>3}/{total_questions}]  ❌  UNEXPECTED: {e}")

                writer.writerow(row)
                csvfile.flush()       # write immediately so you see progress
                all_rows.append(row)
                category_rows.append(row)

                time.sleep(DELAY_SEC)

            print_category_summary(category, category_rows)

    # ── Final summary ────────────────────────────────────────────────────────
    print(f"\n{'=' * 70}")
    print("  OVERALL SUMMARY")
    print(f"{'=' * 70}")

    valid = [r for r in all_rows if r["trust_score"] not in ("", None)]
    errors = [r for r in all_rows if r["error"]]

    if valid:
        avg_T = sum(float(r["trust_score"]) for r in valid) / len(valid)
        avg_G = sum(float(r["grounding_score"]) for r in valid
                    if r["grounding_score"] not in ("", None)) / max(len(valid), 1)
        high   = sum(1 for r in valid if r["confidence_label"] == "HIGH")
        med    = sum(1 for r in valid if r["confidence_label"] == "MEDIUM")
        low    = sum(1 for r in valid if r["confidence_label"] == "LOW")
        insuf  = sum(1 for r in all_rows if r["confidence_label"] == "INSUFFICIENT_CONTEXT")
        m_yes  = sum(1 for r in valid if r["formula_detected"] == "Yes")
        m_pass = sum(1 for r in valid if r["math_result"] == "PASS")
        m_fail = sum(1 for r in valid if r["math_result"] == "FAIL")

        avg_lat = sum(int(r["latency_ms"]) for r in all_rows
                      if r["latency_ms"]) / max(len(all_rows), 1)

        print(f"  Total questions : {total_questions}")
        print(f"  Answered        : {len(valid)}")
        print(f"  Errors          : {len(errors)}")
        print(f"  Avg latency     : {avg_lat:.0f} ms")
        print()
        print(f"  Avg trust T     : {avg_T:.3f}")
        print(f"  Avg grounding G : {avg_G:.3f}")
        print()
        print(f"  HIGH confidence : {high}  ({high/len(valid)*100:.1f}%)")
        print(f"  MEDIUM confidence: {med}  ({med/len(valid)*100:.1f}%)")
        print(f"  LOW confidence  : {low}  ({low/len(valid)*100:.1f}%)")
        print(f"  Insufficient ctx: {insuf}")
        print()
        print(f"  Formula-verified : {m_yes}/{len(valid)}")
        print(f"  Math PASS        : {m_pass}")
        print(f"  Math FAIL        : {m_fail}  ← potential hallucinations")

    print(f"\n  Results saved to: {OUTPUT_CSV}")
    print(f"  Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


if __name__ == "__main__":
    main()