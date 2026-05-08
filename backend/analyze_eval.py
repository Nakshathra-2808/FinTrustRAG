
"""
analyze_eval.py  —  FinTrustRAG IEEE Paper Analysis
====================================================
Run this in your backend folder where eval_results.csv lives:
    python analyze_eval.py

Outputs:
  1. ieee_summary_table.csv   — main results table for your paper
  2. ieee_category_table.csv  — per-category breakdown table
  3. chart_confidence.png     — confidence distribution bar chart
  4. chart_category_trust.png — avg trust score per category
  5. chart_latency.png        — latency distribution histogram
  6. Prints all key stats to console (copy-paste into paper)
"""

import csv
import os
import statistics
from collections import defaultdict

# ── Try to import matplotlib (optional, for charts) ──────────────────────────
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    HAS_PLOT = True
except ImportError:
    HAS_PLOT = False
    print("⚠  matplotlib not installed — skipping charts (pip install matplotlib)")

INPUT_CSV  = "eval_results.csv"
OUT_SUMMARY  = "ieee_summary_table.csv"
OUT_CATEGORY = "ieee_category_table.csv"

# ─────────────────────────────────────────────────────────────────────────────

def load_csv(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows

def safe_float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None

def safe_int(val):
    try:
        return int(val)
    except (TypeError, ValueError):
        return None

def compute_stats(rows):
    """Compute all aggregate stats from rows."""
    total = len(rows)
    answered = [r for r in rows if r.get("confidence_label") not in ("", None)
                and r.get("confidence_label") != "INSUFFICIENT_CONTEXT"
                and r.get("error", "") == ""]
    errors   = [r for r in rows if r.get("error", "") != ""]
    insuf    = [r for r in rows if r.get("confidence_label") == "INSUFFICIENT_CONTEXT"]
    na_rows  = [r for r in rows if r.get("confidence_label") in ("", None)
                and r.get("error", "") == ""]

    valid_trust = [safe_float(r["trust_score"]) for r in answered
                   if safe_float(r["trust_score"]) is not None]
    valid_grnd  = [safe_float(r["grounding_score"]) for r in answered
                   if safe_float(r["grounding_score"]) is not None]

    latencies = [safe_int(r["latency_ms"]) for r in rows
                 if safe_int(r["latency_ms"]) is not None]

    high   = sum(1 for r in answered if r["confidence_label"] == "HIGH")
    medium = sum(1 for r in answered if r["confidence_label"] == "MEDIUM")
    low    = sum(1 for r in answered if r["confidence_label"] == "LOW")

    math_yes  = [r for r in answered if r.get("formula_detected") == "Yes"]
    math_pass = sum(1 for r in math_yes if r.get("math_result") == "PASS")
    math_fail = sum(1 for r in math_yes if r.get("math_result") == "FAIL")

    return {
        "total": total,
        "answered": len(answered),
        "errors": len(errors),
        "insufficient_ctx": len(insuf) + len(na_rows),
        "avg_trust": statistics.mean(valid_trust) if valid_trust else 0,
        "std_trust": statistics.stdev(valid_trust) if len(valid_trust) > 1 else 0,
        "avg_grounding": statistics.mean(valid_grnd) if valid_grnd else 0,
        "high": high,
        "medium": medium,
        "low": low,
        "answer_rate_pct": len(answered) / total * 100 if total else 0,
        "high_pct": high / len(answered) * 100 if answered else 0,
        "math_verified": len(math_yes),
        "math_pass": math_pass,
        "math_fail": math_fail,
        "math_accuracy_pct": math_pass / len(math_yes) * 100 if math_yes else 0,
        "avg_latency_ms": statistics.mean(latencies) if latencies else 0,
        "median_latency_ms": statistics.median(latencies) if latencies else 0,
        "p95_latency_ms": sorted(latencies)[int(len(latencies)*0.95)] if latencies else 0,
    }

def compute_category_stats(rows):
    """Compute per-category stats."""
    cats = defaultdict(list)
    for r in rows:
        cats[r.get("category", "Unknown")].append(r)

    results = []
    for cat, cat_rows in cats.items():
        total_cat = len(cat_rows)
        answered = [r for r in cat_rows
                    if r.get("confidence_label") not in ("", None, "INSUFFICIENT_CONTEXT")
                    and r.get("error", "") == ""]
        insuf = [r for r in cat_rows
                 if r.get("confidence_label") == "INSUFFICIENT_CONTEXT"
                 or (r.get("confidence_label") in ("", None) and r.get("error","") == "")]
        errors = [r for r in cat_rows if r.get("error","") != ""]

        trust_vals = [safe_float(r["trust_score"]) for r in answered
                      if safe_float(r["trust_score"]) is not None]
        grnd_vals  = [safe_float(r["grounding_score"]) for r in answered
                      if safe_float(r["grounding_score"]) is not None]
        lat_vals   = [safe_int(r["latency_ms"]) for r in cat_rows
                      if safe_int(r["latency_ms"]) is not None]

        high   = sum(1 for r in answered if r["confidence_label"] == "HIGH")
        medium = sum(1 for r in answered if r["confidence_label"] == "MEDIUM")
        low    = sum(1 for r in answered if r["confidence_label"] == "LOW")

        math_yes  = [r for r in answered if r.get("formula_detected") == "Yes"]
        math_pass = sum(1 for r in math_yes if r.get("math_result") == "PASS")

        results.append({
            "Category": cat,
            "Total Qs": total_cat,
            "Answered": len(answered),
            "Insuff. Ctx": len(insuf),
            "Errors": len(errors),
            "Answer Rate %": f"{len(answered)/total_cat*100:.1f}" if total_cat else "0",
            "Avg Trust (T)": f"{statistics.mean(trust_vals):.3f}" if trust_vals else "—",
            "Avg Grounding (G)": f"{statistics.mean(grnd_vals):.3f}" if grnd_vals else "—",
            "HIGH": high,
            "MEDIUM": medium,
            "LOW": low,
            "HIGH %": f"{high/len(answered)*100:.1f}" if answered else "0",
            "Math Verified": len(math_yes),
            "Math PASS": math_pass,
            "Math Accuracy %": f"{math_pass/len(math_yes)*100:.1f}" if math_yes else "—",
            "Avg Latency (ms)": f"{statistics.mean(lat_vals):.0f}" if lat_vals else "—",
        })

    # Sort by category order matching the eval script
    order = ["Income Statement","Cash Flow","Balance Sheet",
             "Financial Ratios","Per Share and Equity","YoY and Growth",
             "Business and Operations"]
    results.sort(key=lambda x: order.index(x["Category"]) if x["Category"] in order else 99)
    return results

def print_ieee_stats(stats, cat_stats):
    """Print everything in a format easy to copy into the paper."""
    print("\n" + "="*70)
    print("  IEEE PAPER — KEY STATISTICS")
    print("="*70)

    print(f"""
── System Performance Overview ──
  Total evaluation questions : {stats['total']}
  Successfully answered      : {stats['answered']}  ({stats['answer_rate_pct']:.1f}%)
  Insufficient context (N/A) : {stats['insufficient_ctx']}
  Errors                     : {stats['errors']}

── Confidence Scoring (NCTS) ──
  Avg Trust Score (T)        : {stats['avg_trust']:.3f}  (σ={stats['std_trust']:.3f})
  Avg Grounding Score (G)    : {stats['avg_grounding']:.3f}
  HIGH confidence            : {stats['high']}  ({stats['high_pct']:.1f}% of answered)
  MEDIUM confidence          : {stats['medium']}
  LOW confidence             : {stats['low']}

── Mathematical Verification ──
  Formula-detected responses : {stats['math_verified']}
  Math PASS (correct)        : {stats['math_pass']}
  Math FAIL (hallucinations) : {stats['math_fail']}
  Math accuracy              : {stats['math_accuracy_pct']:.1f}%

── Latency ──
  Average latency            : {stats['avg_latency_ms']:.0f} ms
  Median latency             : {stats['median_latency_ms']:.0f} ms
  95th percentile latency    : {stats['p95_latency_ms']:.0f} ms
""")

    print("── Per-Category Results ──")
    print(f"  {'Category':<28} {'Ans':>4} {'T':>6} {'G':>6} {'HIGH%':>7} {'MathAcc':>8} {'Lat(ms)':>8}")
    print("  " + "-"*68)
    for c in cat_stats:
        print(f"  {c['Category']:<28} {c['Answered']:>4} "
              f"{c['Avg Trust (T)']:>6} {c['Avg Grounding (G)']:>6} "
              f"{c['HIGH %']:>6}% {c['Math Accuracy %']:>8} "
              f"{c['Avg Latency (ms)']:>8}")

def save_summary_csv(stats, path):
    """Save overall summary as a single-row CSV for easy pasting."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Metric", "Value"])
        for k, v in stats.items():
            w.writerow([k, f"{v:.3f}" if isinstance(v, float) else v])
    print(f"\n  ✅  Saved: {path}")

def save_category_csv(cat_stats, path):
    if not cat_stats:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cat_stats[0].keys())
        w.writeheader()
        w.writerows(cat_stats)
    print(f"  ✅  Saved: {path}")

# ── Chart functions ───────────────────────────────────────────────────────────

def chart_confidence(rows):
    answered = [r for r in rows
                if r.get("confidence_label") not in ("","INSUFFICIENT_CONTEXT",None)
                and r.get("error","") == ""]
    labels = ["HIGH","MEDIUM","LOW"]
    counts = [sum(1 for r in answered if r["confidence_label"]==l) for l in labels]
    colors = ["#2ecc71","#f39c12","#e74c3c"]

    fig, ax = plt.subplots(figsize=(6,4))
    bars = ax.bar(labels, counts, color=colors, edgecolor="white", linewidth=1.5)
    for bar, cnt in zip(bars, counts):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
                str(cnt), ha="center", va="bottom", fontweight="bold", fontsize=12)
    ax.set_title("FinTrustRAG — Confidence Distribution", fontsize=13, fontweight="bold")
    ax.set_ylabel("Number of Responses")
    ax.set_ylim(0, max(counts)*1.2 if counts else 10)
    ax.spines[["top","right"]].set_visible(False)
    plt.tight_layout()
    plt.savefig("chart_confidence.png", dpi=150)
    plt.close()
    print("  ✅  Saved: chart_confidence.png")

def chart_category_trust(cat_stats):
    cats   = [c["Category"].replace(" and "," &\n") for c in cat_stats]
    trusts = [float(c["Avg Trust (T)"]) if c["Avg Trust (T)"] != "—" else 0
              for c in cat_stats]

    fig, ax = plt.subplots(figsize=(9,4))
    bars = ax.barh(cats, trusts, color="#3498db", edgecolor="white")
    for bar, val in zip(bars, trusts):
        ax.text(val+0.005, bar.get_y()+bar.get_height()/2,
                f"{val:.3f}", va="center", fontsize=9)
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("Average Trust Score (T)")
    ax.set_title("FinTrustRAG — Avg Trust Score by Category", fontweight="bold")
    ax.axvline(0.9, color="gray", linestyle="--", linewidth=0.8, label="T=0.90 threshold")
    ax.legend(fontsize=8)
    ax.spines[["top","right"]].set_visible(False)
    plt.tight_layout()
    plt.savefig("chart_category_trust.png", dpi=150)
    plt.close()
    print("  ✅  Saved: chart_category_trust.png")

def chart_latency(rows):
    lats = [safe_int(r["latency_ms"]) for r in rows if safe_int(r["latency_ms"]) is not None]
    if not lats:
        return

    fig, ax = plt.subplots(figsize=(7,4))
    ax.hist(lats, bins=30, color="#9b59b6", edgecolor="white", linewidth=0.8)
    ax.axvline(statistics.mean(lats), color="#e74c3c", linestyle="--",
               label=f"Mean = {statistics.mean(lats):.0f}ms")
    ax.axvline(statistics.median(lats), color="#2ecc71", linestyle="--",
               label=f"Median = {statistics.median(lats):.0f}ms")
    ax.set_xlabel("Latency (ms)")
    ax.set_ylabel("Count")
    ax.set_title("FinTrustRAG — Response Latency Distribution", fontweight="bold")
    ax.legend()
    ax.spines[["top","right"]].set_visible(False)
    plt.tight_layout()
    plt.savefig("chart_latency.png", dpi=150)
    plt.close()
    print("  ✅  Saved: chart_latency.png")

def chart_math_verification(stats):
    labels = ["Math PASS\n(Correct)", "Math FAIL\n(Hallucination)", "No Formula\nDetected"]
    values = [
        stats["math_pass"],
        stats["math_fail"],
        stats["answered"] - stats["math_verified"]
    ]
    colors = ["#2ecc71", "#e74c3c", "#bdc3c7"]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Pie chart
    wedge_data = [v for v in values if v > 0]
    wedge_labels = [l for l,v in zip(labels,values) if v > 0]
    wedge_colors = [c for c,v in zip(colors,values) if v > 0]
    ax1.pie(wedge_data, labels=wedge_labels, colors=wedge_colors,
            autopct="%1.1f%%", startangle=90,
            wedgeprops=dict(edgecolor="white", linewidth=1.5))
    ax1.set_title("Math Verification Breakdown", fontweight="bold")

    # Bar chart - trust scores by confidence label
    ax2.bar(labels, values, color=colors, edgecolor="white")
    for i, (bar_val, label) in enumerate(zip(values, labels)):
        ax2.text(i, bar_val + 0.3, str(bar_val), ha="center", fontweight="bold")
    ax2.set_title("Math Check Counts", fontweight="bold")
    ax2.set_ylabel("Count")
    ax2.spines[["top","right"]].set_visible(False)

    plt.tight_layout()
    plt.savefig("chart_math_verification.png", dpi=150)
    plt.close()
    print("  ✅  Saved: chart_math_verification.png")

# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    if not os.path.exists(INPUT_CSV):
        print(f"❌  '{INPUT_CSV}' not found. Make sure you run this from the backend folder.")
        return

    print(f"  Loading {INPUT_CSV}...")
    rows = load_csv(INPUT_CSV)
    print(f"  Loaded {len(rows)} rows.\n")

    stats     = compute_stats(rows)
    cat_stats = compute_category_stats(rows)

    print_ieee_stats(stats, cat_stats)

    print("\n── Saving CSV outputs ──")
    save_summary_csv(stats, OUT_SUMMARY)
    save_category_csv(cat_stats, OUT_CATEGORY)

    if HAS_PLOT:
        print("\n── Generating charts ──")
        chart_confidence(rows)
        chart_category_trust(cat_stats)
        chart_latency(rows)
        chart_math_verification(stats)
    else:
        print("\n  Install matplotlib to get charts:  pip install matplotlib")

    print("\n" + "="*70)
    print("  DONE — Use these files in your IEEE paper:")
    print("    ieee_summary_table.csv    → Table II (Overall Performance)")
    print("    ieee_category_table.csv   → Table III (Per-Category Results)")
    print("    chart_confidence.png      → Figure X (Confidence Distribution)")
    print("    chart_category_trust.png  → Figure X (Trust Score by Category)")
    print("    chart_latency.png         → Figure X (Latency Distribution)")
    print("    chart_math_verification.png → Figure X (Math Hallucination Rate)")
    print("="*70)

if __name__ == "__main__":
    main()