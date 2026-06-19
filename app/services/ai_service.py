import json

import ollama

from app.models import ClauseRisk, RiskLevel

MODEL = "llama3.2:1b"

PROMPT_TEMPLATE = """\
You are a contract risk analysis API.

Analyze the following contract clause and assess its risk for the user
who would sign this contract.

Return a single JSON object with exactly these fields:
- "risk_level": one of "low", "medium", "high"
- "risk_score": an integer from 0 to 10
- "description": 1-2 sentences explaining what the risk is and why it
  affects the user.

Clause:
{clause}
"""


def _extract_json(raw: str) -> dict:
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    # Safety net in case the model still wraps JSON in extra text.
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("No JSON object found in model output")
    return json.loads(cleaned[start:end + 1])


def _safe_level(value: object) -> RiskLevel:
    try:
        return RiskLevel(str(value).lower())
    except ValueError:
        return RiskLevel.unknown


def _safe_score(value: object) -> int:
    try:
        score = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, min(score, 10))


def ping_model() -> str:
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": "Say hello in one short sentence."}],
    )
    return response["message"]["content"]


def analyze_clause(clause: str) -> ClauseRisk:
    response = ollama.chat(
        model=MODEL,
        messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(clause=clause)}],
        format="json",
    )
    raw = response["message"]["content"]

    try:
        data = _extract_json(raw)
    except (ValueError, json.JSONDecodeError):
        return ClauseRisk(clause=clause, description=raw.strip()[:300])

    return ClauseRisk(
        clause=clause,
        risk_level=_safe_level(data.get("risk_level")),
        risk_score=_safe_score(data.get("risk_score")),
        description=str(data.get("description", "")).strip(),
    )
