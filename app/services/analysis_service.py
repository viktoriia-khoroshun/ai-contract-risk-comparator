from app.models import ContractAnalysisResponse, ContractComparison
from app.services.ai_service import analyze_clause
from app.services.pdf_service import (
    extract_text_from_pdf,
    split_text_into_clauses,
)

# MVP limit: analyze only the first N clauses to keep response time sane
# with a local model. Raise/remove once moved to a bigger model or batching.
MAX_CLAUSES = 10


def analyze_contract(filename: str, content: bytes) -> ContractAnalysisResponse:
    text = extract_text_from_pdf(content)
    clauses = split_text_into_clauses(text)
    risks = [analyze_clause(clause) for clause in clauses[:MAX_CLAUSES]]

    return ContractAnalysisResponse(
        filename=filename,
        total_clauses=len(clauses),
        analyzed_clauses=len(risks),
        risks=risks,
    )


def _average_score(analysis: ContractAnalysisResponse) -> float:
    scores = [risk.risk_score for risk in analysis.risks]
    if not scores:
        return 0.0
    return round(sum(scores) / len(scores), 2)


def compare_contracts(
    analysis_a: ContractAnalysisResponse,
    analysis_b: ContractAnalysisResponse,
) -> ContractComparison:
    avg_a = _average_score(analysis_a)
    avg_b = _average_score(analysis_b)

    if avg_a > avg_b:
        riskier = analysis_a.filename
        summary = (
            f"{analysis_a.filename} looks riskier "
            f"(average risk score {avg_a} vs {avg_b})."
        )
    elif avg_b > avg_a:
        riskier = analysis_b.filename
        summary = (
            f"{analysis_b.filename} looks riskier "
            f"(average risk score {avg_b} vs {avg_a})."
        )
    else:
        riskier = "tie"
        summary = f"Both contracts have a similar average risk score ({avg_a})."

    return ContractComparison(
        contract_a=analysis_a,
        contract_b=analysis_b,
        avg_score_a=avg_a,
        avg_score_b=avg_b,
        riskier_contract=riskier,
        summary=summary,
    )
