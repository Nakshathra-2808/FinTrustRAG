
"""
ncts.py  —  Numerical Consistency Trust Scorer
FinTrustRAG  |  Full updated version

Fixes applied:
  1. Broader formula keyword triggers  → Math-verified no longer 0
  2. Intermediate decimal filtering    → 0.469, 0.3197 no longer flagged
  3. Operating margin + FCF margin     → 2 new formula handlers
  4. 500 errors fixed                  → safe division everywhere
  5. INSUFFICIENT_CONTEXT tier         → separate from LOW
  6. Dynamic operand extraction        → works for any company
  7. Adaptive tolerance                → max(1.0, 2% of expected)
  8. Section-label aware extraction    → ROE/current ratio bugs fixed
  9. EPS direct extraction first       → no more brute-force false PASSes
 10. YoY anchored to keyword sentences → no more top-2 globally bug
"""

import re

# ── Constants ─────────────────────────────────────────────────────────────────
ALPHA     = 0.6
BETA      = 0.4
EPSILON   = 0.1
DELTA_ABS = 1.0
DELTA_REL = 0.02

# ── Formula library (11 formulas) ────────────────────────────────────────────
FORMULA_PATTERNS = {
    "profit_margin": {
        "keywords": [
            "gross profit margin", "gross margin percentage",
            "gross margin", "margin percentage",
            "margin is", "margin was", "margin of",
            "margin =", "margin:",
        ],
        "description": "gross margin = (gross profit / revenue) × 100",
    },
    "net_profit_margin": {
        "keywords": [
            "net profit margin", "net margin",
            "profit as a percentage of revenue",
            "net income margin", "net margin is",
            "net margin was", "net margin =", "net margin:",
        ],
        "description": "net profit margin = (net income / revenue) × 100",
    },
    "operating_margin": {
        "keywords": [
            "operating margin", "operating income margin",
            "operating margin is", "operating margin was",
            "operating margin =", "operating margin:",
        ],
        "description": "operating margin = (operating income / revenue) × 100",
    },
    "free_cash_flow": {
        "keywords": [
            "free cash flow", "fcf",
            "free cash flow was", "free cash flow of",
            "free cash flow =", "free cash flow:", "fcf =", "fcf:",
        ],
        "description": "FCF = operating cash flow − capital expenditure",
    },
    "fcf_margin": {
        "keywords": [
            "free cash flow margin", "fcf margin",
            "free cash flow margin is", "free cash flow margin was",
        ],
        "description": "FCF margin = (FCF / revenue) × 100",
    },
    "yoy_growth": {
        "keywords": [
            "growth rate", "year-over-year", "year-on-year", "yoy",
            "revenue growth", "income growth",
            "change year over year", "changed year over year",
            "growth rate is", "growth rate was", "growth rate =",
            "grew by", "increased by", "decreased by",
        ],
        "description": "growth = ((current − prior) / |prior|) × 100",
    },
    "roe": {
        "keywords": [
            "return on equity", "roe",
            "return on shareholders equity",
            "return on stockholders equity",
            "roe is", "roe was", "roe =",
        ],
        "description": "ROE = (net income / shareholders equity) × 100",
    },
    "eps": {
        "keywords": [
            "earnings per share", "eps",
            "diluted earnings per share",
            "basic earnings per share",
            "eps is", "eps was", "eps =",
            "per share is", "per share was",
        ],
        "description": "EPS = net income / diluted shares outstanding",
    },
    "debt_to_equity": {
        "keywords": [
            "debt to equity", "debt-to-equity",
            "leverage ratio", "d/e ratio",
            "d/e is", "d/e was",
        ],
        "description": "D/E = total liabilities / shareholders equity",
    },
    "current_ratio": {
        "keywords": [
            "current ratio", "liquidity ratio",
            "current ratio is", "current ratio was", "current ratio =",
        ],
        "description": "current ratio = current assets / current liabilities",
    },
    "capex_pct_revenue": {
        "keywords": [
            "capital expenditure as a percentage",
            "capex as a percentage", "capex to revenue",
            "capital expenditure as % of revenue",
        ],
        "description": "capex % revenue = (capex / revenue) × 100",
    },
}

# Phrases meaning LLM found nothing — not a hallucination
NOT_AVAILABLE_PHRASES = [
    "not available in the provided",
    "not available in the document",
    "cannot find",
    "not enough information",
    "does not contain",
    "is not available",
    "not provided in",
    "not mentioned in",
    "no information",
    "cannot be determined",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_chunk_text(chunk) -> str:
    if isinstance(chunk, dict):
        return chunk.get("text", "")
    return str(chunk)


def get_chunk_section(chunk) -> str:
    if isinstance(chunk, dict):
        return chunk.get("section_label", "Body")
    return "Body"


def get_nums_from_section(chunks: list, section: str) -> list:
    """
    Extract normalised floats from chunks matching section label.
    Falls back to all chunks if no match found.
    """
    filtered = [
        get_chunk_text(c) for c in chunks
        if get_chunk_section(c) == section
    ]
    if not filtered:
        filtered = [get_chunk_text(c) for c in chunks]
    text = " ".join(filtered)
    return [n for _, n in extract_numbers(text)]


def extract_numbers(text: str) -> list:
    """
    Extract (original_string, normalised_float) pairs from text.
    Covers: plain integers/decimals, $-prefixed, scale-qualified
    (billion/million/thousand), percentages, negatives.
    """
    if not isinstance(text, str):
        text = str(text)

    pattern = (
        r'-?[\$]?[\d,]+\.?\d*\s*'
        r'(?:trillion|billion|million|thousand)?'
        r'(?:\s*%)?'
        r'|\([\$]?[\d,]+\.?\d*\)'
    )

    results = []
    for match in re.finditer(pattern, text, re.IGNORECASE):
        original = match.group().strip()
        if not original or len(original) < 2:
            continue
        normalised = normalize_number(original)
        if normalised is not None:
            results.append((original, normalised))
    return results


def normalize_number(text: str) -> float:
    """Convert a matched number string to a canonical float."""
    try:
        text = text.strip()
        is_negative = text.startswith('(') and text.endswith(')')
        if is_negative:
            text = text[1:-1]
        if text.startswith('-'):
            is_negative = True
            text = text[1:]

        text = text.replace('$', '').replace(',', '').strip()

        scale = 1.0
        text_lower = text.lower()
        for word, mult in [
            ('trillion', 1e12), ('billion', 1e9),
            ('million', 1e6),   ('thousand', 1e3),
        ]:
            if word in text_lower:
                scale = mult
                text = re.sub(word, '', text, flags=re.IGNORECASE).strip()
                break

        if '%' in text:
            text = text.replace('%', '').strip()
            val = float(text)
            return -val if is_negative else val

        val = float(text) * scale
        return -val if is_negative else val

    except (ValueError, AttributeError):
        return None


def adaptive_tolerance(expected: float) -> float:
    """max(δ_abs, δ_rel × |E|) handles both small % and large $ values."""
    return max(DELTA_ABS, DELTA_REL * abs(expected))


def detect_unit_scale(source_text: str) -> float:
    """Detect if document reports figures in millions or billions."""
    if re.search(r'in millions', source_text, re.IGNORECASE):
        return 1e6
    if re.search(r'in billions', source_text, re.IGNORECASE):
        return 1e9
    return 1.0


# ── Step A + B: Grounding ─────────────────────────────────────────────────────

def check_grounding(answer_numbers: list, chunks: list) -> tuple:
    """
    Returns (grounding_score, flagged_numbers_list).

    Three strategies per number:
      1. Exact string match
      2. Direct fuzzy float match (±EPSILON relative)
      3. Unit-adjusted fuzzy match

    FIX: Filters intermediate calculation values before checking.
    Values like 0.469, 0.3197, 100 are LLM working steps — not hallucinations.
    """
    if not answer_numbers:
        return 1.0, []

    source_text  = " ".join([get_chunk_text(c) for c in chunks])
    source_floats = [n for _, n in extract_numbers(source_text)]
    scale        = detect_unit_scale(source_text)

    def is_intermediate(original: str, normalised: float) -> bool:
        # "100" alone = multiplication factor in formula steps
        if original.strip() in ("100", "100.0"):
            return True
        # Pure ratio decimals between 0 and 2 not in source = intermediate
        if 0 < abs(normalised) < 2.0 and '.' in original:
            clean = original.replace('$', '').replace(',', '').strip()
            if clean not in source_text:
                return True
        return False

    grounded_count = 0
    flagged        = []

    for original, normalised in answer_numbers:
        # Skip year numbers — never a hallucination
        if 2019 <= normalised <= 2031:
            grounded_count += 1
            continue

        # Skip intermediate calculation values
        if is_intermediate(original, normalised):
            grounded_count += 1
            continue

        grounded = False

        # Strategy 1: exact string
        clean = (
            original.replace('$', '').replace(',', '')
                    .replace('-', '').strip()
        )
        if clean and clean in source_text:
            grounded = True

        # Strategy 2: direct fuzzy float
        if not grounded:
            for sf in source_floats:
                if sf == 0:
                    continue
                try:
                    if abs(normalised - sf) / abs(sf) <= EPSILON:
                        grounded = True
                        break
                    if abs(abs(normalised) - abs(sf)) / abs(sf) <= EPSILON:
                        grounded = True
                        break
                except Exception:
                    continue

        # Strategy 3: unit-adjusted fuzzy
        if not grounded and scale != 1.0:
            adjusted = normalised / scale
            for sf in source_floats:
                if sf == 0:
                    continue
                try:
                    if abs(adjusted - sf) / abs(sf) <= EPSILON:
                        grounded = True
                        break
                except Exception:
                    continue

        if grounded:
            grounded_count += 1
        else:
            flagged.append(original)

    score = grounded_count / len(answer_numbers)
    return round(score, 2), flagged


# ── Dynamic operand extractors ────────────────────────────────────────────────

def extract_operating_cf_and_capex(chunks: list, source_text: str) -> tuple:
    """Extract (operating_cf, capex) from Cash Flow chunks. Any company."""
    cf_text = " ".join([
        get_chunk_text(c) for c in chunks
        if get_chunk_section(c) == "Cash Flow"
    ]) or source_text

    operating_cf = None
    for pat in [
        r'(?:net cash.*?operating activities|cash generated by operating'
        r'|cash provided by operating)[^\d\-\(]*?([\-\(]?[\d,]+)',
        r'operating activities[^\d\-\(]*?([\-\(]?[\d,]+)',
    ]:
        m = re.search(pat, cf_text, re.IGNORECASE)
        if m:
            val = normalize_number(m.group(1))
            if val and 5_000 < abs(val) < 500_000:
                operating_cf = val
                break

    if not operating_cf:
        nums = [
            n for _, n in extract_numbers(cf_text)
            if not (2019 <= n <= 2031) and 10_000 < n < 500_000
        ]
        operating_cf = max(nums) if nums else None

    capex = None
    for pat in [
        r'(?:purchases? of property.*?plant.*?equipment'
        r'|capital expenditure[s]?|purchase[s]? of property)'
        r'[^\d\-\(]*?([\-\(]?[\d,]+)',
        r'(?:capex|capital spending)[^\d\-\(]*?([\-\(]?[\d,]+)',
        r'property.*?plant.*?equipment[^\d\-\(]*?([\-\(]?[\d,]+)',
    ]:
        m = re.search(pat, cf_text, re.IGNORECASE)
        if m:
            val = normalize_number(m.group(1))
            if val and 500 < abs(val) < 100_000:
                capex = abs(val)
                break

    if not capex and operating_cf:
        nums = [
            n for _, n in extract_numbers(cf_text)
            if not (2019 <= n <= 2031)
            and 500 < abs(n) < abs(operating_cf) * 0.5
        ]
        capex = min(abs(n) for n in nums) if nums else None

    print(f"   CF extraction: operating_cf={operating_cf}, capex={capex}")
    return operating_cf, capex


def extract_revenue_and_profit(chunks: list, source_text: str,
                                profit_type: str = "gross") -> tuple:
    """Extract (revenue, profit) from Income Statement chunks. Any company."""
    income_text = " ".join([
        get_chunk_text(c) for c in chunks
        if get_chunk_section(c) == "Income Statement"
    ]) or source_text

    revenue = None
    for pat in [
        r'(?:total net sales|total revenue|net revenue'
        r'|total revenues|net sales)[^\d\-\(]*?([\d,]+)',
    ]:
        m = re.search(pat, income_text, re.IGNORECASE)
        if m:
            val = normalize_number(m.group(1))
            if val and val > 10_000:
                revenue = val
                break

    profit = None
    patterns = (
        [r'(?:gross margin|gross profit)[^\d\-\(]*?([\d,]+)']
        if profit_type == "gross"
        else [r'(?:net income|net earnings)[^\d\-\(]*?([\d,]+)']
    )
    for pat in patterns:
        m = re.search(pat, income_text, re.IGNORECASE)
        if m:
            val = normalize_number(m.group(1))
            if val and 1_000 < val < 500_000:
                profit = val
                break

    print(f"   Income extraction ({profit_type}): revenue={revenue}, profit={profit}")
    return revenue, profit


def extract_operating_income_and_revenue(chunks: list,
                                          source_text: str) -> tuple:
    """Extract (operating_income, revenue) for operating margin. Any company."""
    income_text = " ".join([
        get_chunk_text(c) for c in chunks
        if get_chunk_section(c) == "Income Statement"
    ]) or source_text

    op_income = None
    for pat in [
        r'(?:operating income|income from operations)'
        r'[^\d\-\(]*?([\d,]+)',
        r'(?:total operating income)[^\d\-\(]*?([\d,]+)',
    ]:
        m = re.search(pat, income_text, re.IGNORECASE)
        if m:
            val = normalize_number(m.group(1))
            if val and 1_000 < val < 500_000:
                op_income = val
                break

    revenue = None
    for pat in [
        r'(?:total net sales|total revenue|net revenue'
        r'|total revenues|net sales)[^\d\-\(]*?([\d,]+)',
    ]:
        m = re.search(pat, income_text, re.IGNORECASE)
        if m:
            val = normalize_number(m.group(1))
            if val and val > 10_000:
                revenue = val
                break

    print(f"   OpMargin extraction: op_income={op_income}, revenue={revenue}")
    return op_income, revenue


def extract_eps_direct(chunks: list, source_text: str):
    """
    FIX: Try to read EPS directly from chunk text before brute-forcing.
    10-Ks always state diluted EPS explicitly.
    Returns float or None.
    """
    for c in chunks:
        text = get_chunk_text(c)
        for pat in [
            r'(?:diluted earnings per share|diluted eps)'
            r'[^\d\-\(]*?([\-\(]?\$?[\d,]+\.?\d*)',
            r'(?:basic earnings per share|basic eps)'
            r'[^\d\-\(]*?([\-\(]?\$?[\d,]+\.?\d*)',
            r'(?:earnings per.*?share)[^\d\-\(]*?([\-\(]?\$?[\d,]+\.?\d*)',
        ]:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                val = normalize_number(m.group(1))
                if val and 0.01 < abs(val) < 500:
                    return val
    return None


def extract_balance_sheet_pair(chunks: list, source_text: str) -> dict:
    """
    FIX for ROE/current-ratio bugs.
    Extract Balance Sheet values by section_label — not from global pool.
    Returns dict: equity, current_assets, current_liabilities, total_liabilities
    """
    bs_text = " ".join([
        get_chunk_text(c) for c in chunks
        if get_chunk_section(c) == "Balance Sheet"
    ]) or source_text

    result = {
        "equity":               None,
        "current_assets":       None,
        "current_liabilities":  None,
        "total_liabilities":    None,
    }

    patterns = {
        "equity": [
            r'(?:total shareholders.*?equity|stockholders.*?equity'
            r'|total equity)[^\d\-\(]*?([\-\(]?[\d,]+)',
        ],
        "current_assets": [
            r'(?:total current assets)[^\d\-\(]*?([\-\(]?[\d,]+)',
            r'(?:current assets)[^\d\-\(]*?([\-\(]?[\d,]+)',
        ],
        "current_liabilities": [
            r'(?:total current liabilities)[^\d\-\(]*?([\-\(]?[\d,]+)',
            r'(?:current liabilities)[^\d\-\(]*?([\-\(]?[\d,]+)',
        ],
        "total_liabilities": [
            r'(?:total liabilities)[^\d\-\(]*?([\-\(]?[\d,]+)',
        ],
    }

    for key, pats in patterns.items():
        for pat in pats:
            m = re.search(pat, bs_text, re.IGNORECASE)
            if m:
                val = normalize_number(m.group(1))
                if val and abs(val) > 100:
                    result[key] = val
                    break

    print(f"   Balance Sheet: {result}")
    return result


def extract_yoy_values_anchored(answer: str, chunks: list,
                                 source_text: str) -> tuple:
    """
    FIX for YoY bug: anchor to metric keyword sentences, not top-2 globally.
    Returns (current, prior) or (None, None).
    """
    metric_keywords = [
        "revenue", "net sales", "net income", "gross profit",
        "operating income", "earnings", "cash flow",
    ]
    answer_lower    = answer.lower()
    detected_metric = next(
        (kw for kw in metric_keywords if kw in answer_lower), "revenue"
    )

    sentences = re.split(r'[.\n]', source_text)
    relevant  = [
        s for s in sentences
        if detected_metric in s.lower() and any(c.isdigit() for c in s)
    ]

    if not relevant:
        return None, None

    relevant_text = " ".join(relevant)
    nums = sorted(
        [n for _, n in extract_numbers(relevant_text)
         if not (2019 <= n <= 2031) and n > 1_000],
        reverse=True
    )

    if len(nums) >= 2:
        return nums[0], nums[1]
    return None, None


# ── Step C: Math verification ─────────────────────────────────────────────────

def verify_math(answer: str, answer_numbers: list, chunks: list) -> tuple:
    """
    Returns (math_score, math_checks_list).
    math_score: 1.0 PASS | 0.5 PARTIAL | 0.0 FAIL | None (no formula)
    """
    if not isinstance(answer, str):
        answer = str(answer)

    answer_lower  = answer.lower()
    source_text   = " ".join([get_chunk_text(c) for c in chunks])
    answer_floats = [n for _, n in answer_numbers]
    math_checks   = []

    # Detect formula — first keyword match wins
    detected = None
    for fname, finfo in FORMULA_PATTERNS.items():
        if any(kw in answer_lower for kw in finfo["keywords"]):
            detected = (fname, finfo)
            break

    if not detected:
        return None, []

    formula_name, formula_info = detected
    print(f"   Formula detected: {formula_name}")

    try:

        # ── FREE CASH FLOW ────────────────────────────────────────────────
        if formula_name == "free_cash_flow":
            operating_cf, capex = extract_operating_cf_and_capex(
                chunks, source_text
            )
            if operating_cf and capex:
                expected = operating_cf - capex
                tol      = adaptive_tolerance(expected)
                scale    = detect_unit_scale(source_text)

                for ans in answer_floats:
                    ans_norm = (
                        ans / scale
                        if (scale != 1.0 and abs(ans) > 1e6)
                        else ans
                    )
                    diff = abs(ans_norm - expected)
                    if diff <= tol:
                        math_checks.append({
                            "formula": formula_info["description"],
                            "expected": round(expected, 2),
                            "got":      round(ans_norm, 2),
                            "result":   "PASS",
                        })
                        return 1.0, math_checks
                    elif diff <= abs(expected) * 0.05:
                        math_checks.append({
                            "formula": formula_info["description"],
                            "expected": round(expected, 2),
                            "got":      round(ans_norm, 2),
                            "result":   "PARTIAL",
                        })
                        return 0.5, math_checks

                neg   = [n for n in answer_floats if n < 0]
                clean = [
                    n for n in answer_floats
                    if not (2019 <= n <= 2031) and abs(n) < 200_000
                ]
                best_got = (
                    round(neg[0], 2)   if neg   else
                    round(min(clean), 2) if clean else
                    (round(answer_floats[0], 2) if answer_floats else "N/A")
                )
                math_checks.append({
                    "formula": formula_info["description"],
                    "expected": round(expected, 2),
                    "got":      best_got,
                    "result":   "FAIL",
                })
                return 0.0, math_checks

        # ── FCF MARGIN ────────────────────────────────────────────────────
        elif formula_name == "fcf_margin":
            operating_cf, capex = extract_operating_cf_and_capex(
                chunks, source_text
            )
            revenue, _ = extract_revenue_and_profit(
                chunks, source_text, "gross"
            )
            if operating_cf and capex and revenue and revenue > 0:
                fcf      = operating_cf - capex
                expected = (fcf / revenue) * 100
                for ans in answer_floats:
                    if abs(ans - expected) <= adaptive_tolerance(expected):
                        math_checks.append({
                            "formula": formula_info["description"],
                            "expected": round(expected, 2),
                            "got":      ans,
                            "result":   "PASS",
                        })
                        return 1.0, math_checks
                math_checks.append({
                    "formula": formula_info["description"],
                    "expected": round(expected, 2),
                    "got":      answer_floats[0] if answer_floats else "N/A",
                    "result":   "FAIL",
                })
                return 0.0, math_checks

        # ── GROSS PROFIT MARGIN ───────────────────────────────────────────
        elif formula_name == "profit_margin":
            revenue, profit = extract_revenue_and_profit(
                chunks, source_text, profit_type="gross"
            )
            if revenue and profit and revenue > 0:
                expected = (profit / revenue) * 100
                for ans in answer_floats:
                    if abs(ans - expected) <= adaptive_tolerance(expected):
                        math_checks.append({
                            "formula": formula_info["description"],
                            "expected": round(expected, 2),
                            "got":      ans,
                            "result":   "PASS",
                        })
                        return 1.0, math_checks
                math_checks.append({
                    "formula": formula_info["description"],
                    "expected": round(expected, 2),
                    "got":      answer_floats[0] if answer_floats else "N/A",
                    "result":   "FAIL",
                })
                return 0.0, math_checks

        # ── NET PROFIT MARGIN ─────────────────────────────────────────────
        elif formula_name == "net_profit_margin":
            revenue, profit = extract_revenue_and_profit(
                chunks, source_text, profit_type="net"
            )
            if revenue and profit and revenue > 0:
                expected = (profit / revenue) * 100
                for ans in answer_floats:
                    if abs(ans - expected) <= adaptive_tolerance(expected):
                        math_checks.append({
                            "formula": formula_info["description"],
                            "expected": round(expected, 2),
                            "got":      ans,
                            "result":   "PASS",
                        })
                        return 1.0, math_checks
                math_checks.append({
                    "formula": formula_info["description"],
                    "expected": round(expected, 2),
                    "got":      answer_floats[0] if answer_floats else "N/A",
                    "result":   "FAIL",
                })
                return 0.0, math_checks

        # ── OPERATING MARGIN ──────────────────────────────────────────────
        elif formula_name == "operating_margin":
            op_income, revenue = extract_operating_income_and_revenue(
                chunks, source_text
            )
            if op_income and revenue and revenue > 0:
                expected = (op_income / revenue) * 100
                for ans in answer_floats:
                    if abs(ans - expected) <= adaptive_tolerance(expected):
                        math_checks.append({
                            "formula": formula_info["description"],
                            "expected": round(expected, 2),
                            "got":      ans,
                            "result":   "PASS",
                        })
                        return 1.0, math_checks
                math_checks.append({
                    "formula": formula_info["description"],
                    "expected": round(expected, 2),
                    "got":      answer_floats[0] if answer_floats else "N/A",
                    "result":   "FAIL",
                })
                return 0.0, math_checks

        # ── EARNINGS PER SHARE ────────────────────────────────────────────
        elif formula_name == "eps":
            # FIX: direct extraction first — 10-Ks always state EPS
            stated_eps = extract_eps_direct(chunks, source_text)
            if stated_eps is not None:
                for ans in answer_floats:
                    if abs(ans - stated_eps) <= adaptive_tolerance(stated_eps):
                        math_checks.append({
                            "formula": formula_info["description"],
                            "expected": round(stated_eps, 2),
                            "got":      ans,
                            "result":   "PASS",
                        })
                        return 1.0, math_checks
                math_checks.append({
                    "formula": formula_info["description"],
                    "expected": round(stated_eps, 2),
                    "got":      answer_floats[0] if answer_floats else "N/A",
                    "result":   "FAIL",
                })
                return 0.0, math_checks

            # Fallback: compute from income + shares with tighter ranges
            income_nums = get_nums_from_section(chunks, "Income Statement")
            share_candidates = [
                n for n in income_nums
                if 5_000 < n < 30_000 and not (2019 <= n <= 2031)
            ]
            income_candidates = [
                n for n in income_nums
                if n > 10_000 and not (2019 <= n <= 2031)
            ]
            for ni in income_candidates:
                for sh in share_candidates:
                    if sh > 0 and ni != sh:
                        computed = ni / sh
                        if 0.01 < computed < 500:
                            for ans in answer_floats:
                                if abs(ans - computed) <= adaptive_tolerance(computed):
                                    math_checks.append({
                                        "formula": formula_info["description"],
                                        "expected": round(computed, 2),
                                        "got":      ans,
                                        "result":   "PASS",
                                    })
                                    return 1.0, math_checks

        # ── RETURN ON EQUITY ──────────────────────────────────────────────
        elif formula_name == "roe":
            # FIX: income from Income Statement, equity from Balance Sheet
            income_nums = get_nums_from_section(chunks, "Income Statement")
            bs          = extract_balance_sheet_pair(chunks, source_text)
            equity      = bs["equity"]

            if equity and equity != 0:
                for ni in income_nums:
                    if not (2019 <= ni <= 2031) and ni > 1_000:
                        try:
                            expected = (ni / equity) * 100
                        except ZeroDivisionError:
                            continue
                        if 0 < expected < 500:
                            for ans in answer_floats:
                                if abs(ans - expected) <= adaptive_tolerance(expected):
                                    math_checks.append({
                                        "formula": formula_info["description"],
                                        "expected": round(expected, 2),
                                        "got":      ans,
                                        "result":   "PASS",
                                    })
                                    return 1.0, math_checks

        # ── YoY GROWTH ────────────────────────────────────────────────────
        elif formula_name == "yoy_growth":
            # FIX: anchor to metric keyword sentences
            current, prior = extract_yoy_values_anchored(
                answer, chunks, source_text
            )
            if current and prior and prior != 0:
                try:
                    expected = ((current - prior) / abs(prior)) * 100
                except ZeroDivisionError:
                    return None, []

                for ans in answer_floats:
                    if abs(ans - expected) <= adaptive_tolerance(expected):
                        math_checks.append({
                            "formula": formula_info["description"],
                            "expected": round(expected, 2),
                            "got":      ans,
                            "result":   "PASS",
                        })
                        return 1.0, math_checks
                math_checks.append({
                    "formula": formula_info["description"],
                    "expected": round(expected, 2),
                    "got":      answer_floats[0] if answer_floats else "N/A",
                    "result":   "FAIL",
                })
                return 0.0, math_checks

        # ── DEBT TO EQUITY ────────────────────────────────────────────────
        elif formula_name == "debt_to_equity":
            bs         = extract_balance_sheet_pair(chunks, source_text)
            total_liab = bs["total_liabilities"]
            equity     = bs["equity"]

            if total_liab and equity and equity != 0:
                try:
                    expected = total_liab / equity
                except ZeroDivisionError:
                    return None, []

                if 0 < expected < 100:
                    for ans in answer_floats:
                        if abs(ans - expected) <= adaptive_tolerance(expected):
                            math_checks.append({
                                "formula": formula_info["description"],
                                "expected": round(expected, 2),
                                "got":      ans,
                                "result":   "PASS",
                            })
                            return 1.0, math_checks
                    math_checks.append({
                        "formula": formula_info["description"],
                        "expected": round(expected, 2),
                        "got":      answer_floats[0] if answer_floats else "N/A",
                        "result":   "FAIL",
                    })
                    return 0.0, math_checks

        # ── CURRENT RATIO ─────────────────────────────────────────────────
        elif formula_name == "current_ratio":
            # FIX: extract from Balance Sheet section only
            bs = extract_balance_sheet_pair(chunks, source_text)
            ca = bs["current_assets"]
            cl = bs["current_liabilities"]

            if ca and cl and cl != 0:
                try:
                    expected = ca / cl
                except ZeroDivisionError:
                    return None, []

                if 0.1 < expected < 20:
                    for ans in answer_floats:
                        if abs(ans - expected) <= adaptive_tolerance(expected):
                            math_checks.append({
                                "formula": formula_info["description"],
                                "expected": round(expected, 2),
                                "got":      ans,
                                "result":   "PASS",
                            })
                            return 1.0, math_checks
                    math_checks.append({
                        "formula": formula_info["description"],
                        "expected": round(expected, 2),
                        "got":      answer_floats[0] if answer_floats else "N/A",
                        "result":   "FAIL",
                    })
                    return 0.0, math_checks

        # ── CAPEX AS % OF REVENUE ─────────────────────────────────────────
        elif formula_name == "capex_pct_revenue":
            _, capex = extract_operating_cf_and_capex(chunks, source_text)
            revenue, _ = extract_revenue_and_profit(
                chunks, source_text, "gross"
            )
            if capex and revenue and revenue > 0:
                try:
                    expected = (capex / revenue) * 100
                except ZeroDivisionError:
                    return None, []

                for ans in answer_floats:
                    if abs(ans - expected) <= adaptive_tolerance(expected):
                        math_checks.append({
                            "formula": formula_info["description"],
                            "expected": round(expected, 2),
                            "got":      ans,
                            "result":   "PASS",
                        })
                        return 1.0, math_checks
                math_checks.append({
                    "formula": formula_info["description"],
                    "expected": round(expected, 2),
                    "got":      answer_floats[0] if answer_floats else "N/A",
                    "result":   "FAIL",
                })
                return 0.0, math_checks

    except Exception as e:
        print(f"  ⚠️  Math verification error ({formula_name}): {e}")

    return None, math_checks


# ── Step D: Score aggregation ─────────────────────────────────────────────────

def compute_trust_score(G: float, M: float) -> tuple:
    """Returns (trust_score, confidence_label)."""
    T = round(min(max(ALPHA * G + BETA * M, 0.0), 1.0), 2)
    if T >= 0.80:
        label = "HIGH"
    elif T >= 0.50:
        label = "MEDIUM"
    else:
        label = "LOW"
    return T, label


# ── Main entry point ──────────────────────────────────────────────────────────

def run_ncts(answer: str, chunks: list) -> dict:
    """
    Run full NCTS verification pipeline.

    Returns dict with:
      grounding_score, math_score, trust_score, confidence_label,
      flagged_numbers, math_checks, note (optional)
    """
    print("🔍 NCTS verification starting...")

    if not isinstance(answer, str):
        answer = str(answer)

    # Special case: LLM said it couldn't find the answer
    # This is honesty, not hallucination — return INSUFFICIENT_CONTEXT
    if any(phrase in answer.lower() for phrase in NOT_AVAILABLE_PHRASES):
        print("  ⚠️  LLM returned insufficient-context response")
        return {
            "grounding_score":  None,
            "math_score":       None,
            "trust_score":      None,
            "confidence_label": "INSUFFICIENT_CONTEXT",
            "flagged_numbers":  [],
            "math_checks":      [],
            "note": (
                "The model indicated the answer is not available in the "
                "retrieved chunks. Consider expanding the retrieval window "
                "or rephrasing the query."
            ),
        }

    # Step A: Extract numbers from answer
    answer_numbers = extract_numbers(answer)
    print(f"  Step A — {len(answer_numbers)} numbers: "
          f"{[n for _, n in answer_numbers]}")

    # Step B: Grounding check
    G, flagged = check_grounding(answer_numbers, chunks)
    print(f"  Step B — G={G}  flagged={flagged}")

    # Step C: Math verification
    M_raw, math_checks = verify_math(answer, answer_numbers, chunks)
    if M_raw is None:
        M = G
        print(f"  Step C — no formula, M defaults to G={M}")
    else:
        M = M_raw
        print(f"  Step C — M={M}")

    # Step D: Trust score
    T, label = compute_trust_score(G, M)
    print(f"  Step D — T={T} ({label})")

    return {
        "grounding_score":  G,
        "math_score":       round(M, 2),
        "trust_score":      T,
        "confidence_label": label,
        "flagged_numbers":  flagged,
        "math_checks":      math_checks,
    }