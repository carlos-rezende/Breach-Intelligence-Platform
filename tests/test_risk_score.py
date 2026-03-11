"""Testes do cálculo de risk score."""

import pytest

from app.utils.risk_score import calculate_risk_score


@pytest.mark.parametrize(
    "breach_count,expected",
    [
        (0, "safe"),
        (1, "low"),
        (2, "low"),
        (3, "medium"),
        (4, "medium"),
        (5, "medium"),
        (6, "high"),
        (10, "high"),
        (100, "high"),
    ],
)
def test_calculate_risk_score(breach_count: int, expected: str):
    """Testa o cálculo do score de risco."""
    assert calculate_risk_score(breach_count) == expected
