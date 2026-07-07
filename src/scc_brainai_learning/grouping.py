"""Regroupement des signaux en **patterns** récurrents (déterministe)."""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List

from scc_brainai_learning.core.config import LearningConfig
from scc_brainai_learning.core.model import LearningPattern, LearningSignal
from scc_brainai_learning.scoring import impact

_CATEGORY_LABEL = {
    "intent_recurrence": "Récurrence d'intentions",
    "workflow_frequency": "Fréquence de workflows",
    "agent_mobilization": "Mobilisation d'agents",
    "error_recurrence": "Erreurs récurrentes",
    "preference_stability": "Stabilité des préférences",
    "preference_conflict": "Conflits de préférences",
    "weak_zone": "Zones faibles",
}


def group_signals(signals: List[LearningSignal], config: LearningConfig) -> List[LearningPattern]:
    by_cat: Dict[str, List[LearningSignal]] = defaultdict(list)
    for s in signals:
        by_cat[s.data.get("category", "autre")].append(s)

    patterns: List[LearningPattern] = []
    for cat, sigs in sorted(by_cat.items()):
        evidence = sorted({eid for s in sigs for eid in s.evidence})
        freq = sum(s.frequency for s in sigs)
        conf = round(max((s.confidence for s in sigs), default=0.0), 3)
        pat = LearningPattern(
            title=f"Pattern : {_CATEGORY_LABEL.get(cat, cat)}",
            detail=f"{len(sigs)} signal(aux) regroupé(s) sous la catégorie « {cat} ».",
            evidence=evidence, frequency=freq, confidence=conf, impact=impact(cat),
            created_at=config.as_of, tags=["pattern", cat],
            data={"category": cat, "signals": sorted(s.id for s in sigs),
                  "signal_count": len(sigs)},
        )
        patterns.append(pat.finalize())
    return sorted(patterns, key=lambda p: p.id)


__all__ = ["group_signals"]
