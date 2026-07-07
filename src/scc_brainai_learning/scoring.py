"""Scoring déterministe : confiance, fréquence, impact.

Formules pures et bornées. La **confiance** combine la fréquence absolue (vs un
seuil fort) et la consistance (proportion sur le total observé). L'**impact** est
une pondération par catégorie (les erreurs et zones faibles pèsent plus).
"""

from __future__ import annotations


def freq_confidence(frequency: int, strong: int) -> float:
    if strong <= 0:
        return 0.0
    return min(1.0, round(frequency / strong, 3))


def ratio_confidence(count: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(count / total, 3)


def confidence(frequency: int, count: int, total: int, strong: int) -> float:
    """Confiance = moyenne (fréquence normalisée, consistance)."""
    return round(0.5 * freq_confidence(frequency, strong) + 0.5 * ratio_confidence(count, total), 3)


# Pondérations d'impact par catégorie (bornées [0,1]).
_IMPACT = {
    "error_recurrence": 0.9,
    "weak_zone": 0.8,
    "intent_recurrence": 0.5,
    "workflow_frequency": 0.5,
    "agent_mobilization": 0.4,
    "preference_stability": 0.2,
    "preference_conflict": 0.6,
}


def impact(category: str) -> float:
    return _IMPACT.get(category, 0.3)


__all__ = ["freq_confidence", "ratio_confidence", "confidence", "impact"]
