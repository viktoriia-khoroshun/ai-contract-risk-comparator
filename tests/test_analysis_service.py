from app.models import ClauseRisk, ContractAnalysisResponse
from app.services.analysis_service import _average_score, compare_contracts


def _make_analysis(filename: str, scores: list[int]) -> ContractAnalysisResponse:
    return ContractAnalysisResponse(
        filename=filename,
        total_clauses=len(scores),
        analyzed_clauses=len(scores),
        risks=[ClauseRisk(clause="clause", risk_score=score) for score in scores],
    )


def test_average_score():
    analysis = _make_analysis("a.pdf", [8, 6, 7])
    assert _average_score(analysis) == 7.0


def test_average_score_empty_is_zero():
    analysis = _make_analysis("a.pdf", [])
    assert _average_score(analysis) == 0.0


def test_compare_contract_a_riskier():
    a = _make_analysis("a.pdf", [8, 9, 7])
    b = _make_analysis("b.pdf", [1, 2, 1])
    result = compare_contracts(a, b)
    assert result.riskier_contract == "a.pdf"
    assert result.avg_score_a > result.avg_score_b


def test_compare_contract_b_riskier():
    a = _make_analysis("a.pdf", [1, 1, 1])
    b = _make_analysis("b.pdf", [9, 8, 9])
    result = compare_contracts(a, b)
    assert result.riskier_contract == "b.pdf"


def test_compare_tie():
    a = _make_analysis("a.pdf", [5, 5])
    b = _make_analysis("b.pdf", [5, 5])
    result = compare_contracts(a, b)
    assert result.riskier_contract == "tie"
