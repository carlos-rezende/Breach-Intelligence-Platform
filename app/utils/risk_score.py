"""Cálculo do score de risco."""

def calculate_risk_score(breach_count: int) -> str:
    """
    0 breaches → safe
    1-2 → low
    3-5 → medium
    6+ → high
    """
    if breach_count == 0:
        return "safe"
    if breach_count <= 2:
        return "low"
    if breach_count <= 5:
        return "medium"
    return "high"
