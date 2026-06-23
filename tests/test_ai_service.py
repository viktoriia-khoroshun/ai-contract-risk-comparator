import pytest

from app.models import RiskLevel
from app.services.ai_service import _extract_json, _safe_level, _safe_score


def test_safe_level_valid_values():
    assert _safe_level("low") == RiskLevel.low
    assert _safe_level("HIGH") == RiskLevel.high
    assert _safe_level("Medium") == RiskLevel.medium


def test_safe_level_invalid_returns_unknown():
    assert _safe_level("nonsense") == RiskLevel.unknown
    assert _safe_level(None) == RiskLevel.unknown


def test_safe_score_parses_and_clamps():
    assert _safe_score(5) == 5
    assert _safe_score("7") == 7
    assert _safe_score(99) == 10
    assert _safe_score(-3) == 0


def test_safe_score_invalid_returns_zero():
    assert _safe_score("abc") == 0
    assert _safe_score(None) == 0


def test_extract_json_clean():
    raw = '{"risk_level": "low", "risk_score": 1, "description": "ok"}'
    assert _extract_json(raw) == {
        "risk_level": "low",
        "risk_score": 1,
        "description": "ok",
    }


def test_extract_json_with_surrounding_text():
    raw = 'Here is the result:\n{"risk_level": "high"}\nThanks!'
    assert _extract_json(raw) == {"risk_level": "high"}


def test_extract_json_no_object_raises():
    with pytest.raises(ValueError):
        _extract_json("no json here")
