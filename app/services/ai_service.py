import json

import ollama

from app.models import ClauseRisk, RiskLevel

MODEL = "llama3.2:1b"

PROMPT_TEMPLATE = """\
You are a contract risk analysis API.

Analyze the following contract clause and assess its risk for the user
who would sign this contract.

IMPORTANT RULES:
- Return ONLY pure JSON, nothing else.
- Do NOT use markdown or code fences.
- Do NOT add any text outside the JSON object.

Return exactly this JSON format:
{{
    "risk_level": "low | medium | high",
    "risk_score": 1,
    "description": "Explain the risk in 1-2 sentences: what it is and why it affects the user."
}}

Clause:
{clause}
"""


def _clean_model_output(raw: str) -> str:
    return raw.replace("```json", "").replace("```", "").strip()


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
    )

    raw = _clean_model_output(response["message"]["content"])

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Tiny model sometimes breaks JSON — keep the run alive instead of 500.
        return ClauseRisk(clause=clause, description=raw[:300])

    return ClauseRisk(
        clause=clause,
        risk_level=_safe_level(data.get("risk_level")),
        risk_score=_safe_score(data.get("risk_score")),
        description=str(data.get("description", "")).strip(),
    )
