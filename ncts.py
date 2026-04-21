# ncts.py
import re

GROUNDING_WEIGHT = 0.6
MATH_WEIGHT      = 0.4
HIGH_THRESHOLD   = 0.80
MEDIUM_THRESHOLD = 0.50

def extract_numbers(text: str) -> list:
    pattern = r'\$?[\d,]+\.?\d*[BMK%]?'
    raw = re.findall(pattern, text)
    numbers = []
    for n in raw:
        cleaned = n.replace('$', '').replace(',', '').strip('.,')
        if re.match(r'^20[0-9]{2}$', cleaned):
            continue
        if len(cleaned) < 2:
            continue
        numbers.append(cleaned)
    return list(set(numbers))

def check_grounding(answer_numbers: list, chunks: list) -> dict:
    if not answer_numbers:
        return {"grounding_score": 1.0, "grounded": [], "ungrounded": []}
    all_chunk_text = " ".join(c["text"] for c in chunks)
    all_chunk_text_clean = all_chunk_text.replace(',', '').replace('$', '')
    grounded   = []
    ungrounded = []
    for num in answer_numbers:
        num_clean = num.replace(',', '').replace('$', '')
        if num_clean in all_chunk_text_clean:
            grounded.append(num)
        else:
            ungrounded.append(num)
    score = len(grounded) / len(answer_numbers)
    return {"grounding_score": round(score, 3), "grounded": grounded, "ungrounded": ungrounded}

def check_math(answer: str) -> dict:
    math_checks = []
    pct_pattern = r'([\d.]+)%.*?from\s+\$?([\d,]+).*?to\s+\$?([\d,]+)'
    matches = re.findall(pct_pattern, answer, re.IGNORECASE)
    for match in matches:
        try:
            pct    = float(match[0])
            base   = float(match[1].replace(',', ''))
            result = float(match[2].replace(',', ''))
            expected = round(base * (1 + pct / 100), 1)
            tolerance = base * 0.02
            is_correct = abs(result - expected) <= tolerance
            math_checks.append({"claim": f"{pct}% from {base} to {result}", "correct": is_correct})
        except (ValueError, ZeroDivisionError):
            continue
    if not math_checks:
        return {"math_score": 1.0, "checks": []}
    correct = sum(1 for c in math_checks if c["correct"])
    return {"math_score": round(correct / len(math_checks), 3), "checks": math_checks}

def get_confidence_label(trust_score: float) -> str:
    if trust_score >= HIGH_THRESHOLD:
        return "HIGH"
    elif trust_score >= MEDIUM_THRESHOLD:
        return "MEDIUM"
    return "LOW"

def compute_ncts(answer: str, chunks: list) -> dict:
    print("🔍 Running NCTS...")
    answer_numbers = extract_numbers(answer)
    grounding_result = check_grounding(answer_numbers, chunks)
    G = grounding_result["grounding_score"]
    math_result = check_math(answer)
    M = math_result["math_score"]
    T = round(GROUNDING_WEIGHT * G + MATH_WEIGHT * M, 3)
    label = get_confidence_label(T)
    print(f"   G={G}, M={M}, T={T} → {label}")
    return {
        "grounding_score":  G,
        "math_score":       M,
        "trust_score":      T,
        "confidence_label": label,
        "flagged_numbers":  grounding_result["ungrounded"],
        "math_checks":      math_result["checks"]
    }