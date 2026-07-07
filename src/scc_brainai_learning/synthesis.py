"""Synthèse : patterns → **leçons**, **recommandations**, **hypothèses**.

Dérivations déterministes par règles. **Tout est propositionnel** : une
recommandation ou une hypothèse n'est jamais appliquée — elle attend une validation
humaine et reste révocable. Chaque dérivation cite le pattern et les événements
sources (traçabilité).
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from scc_brainai_learning.core.config import LearningConfig
from scc_brainai_learning.core.model import (
    LearningHypothesis,
    LearningLesson,
    LearningPattern,
    LearningRecommendation,
)

# category -> (leçon, recommandation|None, hypothèse|None)
_TEMPLATES: Dict[str, Dict[str, str]] = {
    "intent_recurrence": {
        "lesson": "Certaines intentions dominent l'usage : BrainAI est sollicité de façon récurrente sur ces axes.",
    },
    "workflow_frequency": {
        "lesson": "Des séquences d'actions reviennent souvent : ce sont des workflows de fait.",
        "reco": "Proposer de formaliser les séquences d'actions les plus fréquentes en workflow nommé (proposition).",
        "hypo": "Hypothèse : nommer et outiller les séquences fréquentes réduirait la variabilité d'exécution.",
    },
    "agent_mobilization": {
        "lesson": "Un petit nombre d'agents est mobilisé de façon récurrente (dont le superviseur, incarné par BrainAI).",
        "reco": "Bonne pratique proposée : documenter les agents pivots comme dépendances clés des intentions.",
    },
    "error_recurrence": {
        "lesson": "Des erreurs se répètent : elles constituent une dette de fiabilité à traiter.",
        "reco": "Proposer d'ajouter une vérification préalable ciblant l'erreur récurrente (proposition, non appliquée).",
        "hypo": "Hypothèse : traiter l'erreur récurrente en amont supprimerait la majorité des échecs observés.",
    },
    "weak_zone": {
        "lesson": "Des zones faibles ressortent (taux d'erreur, faible diversité) : points d'attention prioritaires.",
        "reco": "Proposer un plan d'amélioration ciblé sur la zone faible identifiée (proposition à valider).",
        "hypo": "Hypothèse : renforcer la zone faible améliorerait la robustesse globale du Kernel.",
    },
    "preference_stability": {
        "lesson": "Des préférences non sensibles sont stables : elles peuvent servir de valeurs par défaut.",
        "reco": "Proposer d'adopter les préférences stables comme réglages par défaut (proposition révocable).",
    },
    "preference_conflict": {
        "lesson": "Des préférences fluctuent : source d'incohérence potentielle.",
        "reco": "Proposer de clarifier la préférence conflictuelle avec l'utilisateur (proposition).",
        "hypo": "Hypothèse : fixer la préférence conflictuelle réduirait l'incohérence perçue.",
    },
}


def synthesize(patterns: List[LearningPattern], config: LearningConfig
               ) -> Tuple[List[LearningLesson], List[LearningRecommendation], List[LearningHypothesis]]:
    lessons: List[LearningLesson] = []
    recommendations: List[LearningRecommendation] = []
    hypotheses: List[LearningHypothesis] = []

    for pat in patterns:
        cat = pat.data.get("category", "")
        tpl = _TEMPLATES.get(cat)
        if not tpl:
            continue
        base = dict(evidence=pat.evidence, frequency=pat.frequency,
                    confidence=pat.confidence, impact=pat.impact, created_at=config.as_of)

        lessons.append(LearningLesson(
            title=f"Leçon : {_label(cat)}", detail=tpl["lesson"],
            tags=["lesson", cat], data={"category": cat, "from_pattern": pat.id}, **base).finalize())

        if "reco" in tpl:
            recommendations.append(LearningRecommendation(
                title=f"Recommandation : {_label(cat)}", detail=tpl["reco"],
                tags=["recommendation", cat, "proposal"],
                data={"category": cat, "from_pattern": pat.id, "applied": False}, **base).finalize())

        if "hypo" in tpl:
            hypotheses.append(LearningHypothesis(
                title=f"Hypothèse : {_label(cat)}", detail=tpl["hypo"],
                tags=["hypothesis", cat, "proposal"],
                data={"category": cat, "from_pattern": pat.id, "testable": True}, **base).finalize())

    return (sorted(lessons, key=lambda x: x.id),
            sorted(recommendations, key=lambda x: x.id),
            sorted(hypotheses, key=lambda x: x.id))


def _label(cat: str) -> str:
    return cat.replace("_", " ")


__all__ = ["synthesize"]
