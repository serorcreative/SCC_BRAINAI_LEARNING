"""Modèle de la couche d'apprentissage BrainAI.

Tous les apprentissages sont des **propositions** : traçables (vers les événements
mémoire sources), vérifiables (empreinte de contenu), et **révocables** (cycle de
validation humaine). Rien n'est jamais appliqué automatiquement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar, Dict, List

from scc_brainai_learning.core.clock import digest, short_id


class LearningKind(str, Enum):
    SIGNAL = "signal"                 # observation atomique / signal faible
    PATTERN = "pattern"               # régularité récurrente
    LESSON = "lesson"                 # leçon apprise (lisible)
    RECOMMENDATION = "recommendation" # recommandation actionnable (proposée)
    HYPOTHESIS = "hypothesis"         # hypothèse d'amélioration (à tester)


class LearningStatus(str, Enum):
    """Cycle de validation humaine — aucun apprentissage n'est auto-appliqué."""

    PROPOSED = "proposed"     # produit par l'analyse ; en attente d'un humain
    VALIDATED = "validated"   # approuvé par un humain
    REJECTED = "rejected"     # écarté par un humain
    REVOKED = "revoked"       # approuvé puis retiré par un humain


# Transitions autorisées (gardées ; l'analyse ne peut que produire 'proposed').
_TRANSITIONS = {
    "proposed": {"validated", "rejected"},
    "validated": {"revoked"},
    "rejected": set(),
    "revoked": set(),
}


def can_transition(current: str, target: str) -> bool:
    return target in _TRANSITIONS.get(current, set())


@dataclass
class LearningItem:
    """Apprentissage propositionnel de base."""

    title: str = ""
    detail: str = ""
    evidence: List[str] = field(default_factory=list)   # ids d'entrées mémoire sources
    confidence: float = 0.0
    frequency: int = 0
    impact: float = 0.0
    status: str = LearningStatus.PROPOSED.value
    created_at: str = ""
    tags: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    validation: Dict[str, Any] = field(default_factory=dict)
    id: str = ""
    hash: str = ""

    KIND: ClassVar[str] = "item"

    @property
    def kind(self) -> str:
        return type(self).KIND

    def _content(self) -> Dict[str, Any]:
        return {"kind": self.kind, "title": self.title, "detail": self.detail,
                "evidence": sorted(self.evidence), "data": self.data}

    def finalize(self) -> "LearningItem":
        """Calcule l'identifiant (déterministe, dérivé du contenu) et l'empreinte."""
        self.id = short_id(self.kind, self._content())
        self.hash = digest({**self._content(), "confidence": self.confidence,
                            "frequency": self.frequency, "impact": self.impact})
        return self

    def verify(self) -> bool:
        expect = digest({**self._content(), "confidence": self.confidence,
                        "frequency": self.frequency, "impact": self.impact})
        return self.hash == expect

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "kind": self.kind, "title": self.title, "detail": self.detail,
            "evidence": list(self.evidence), "confidence": self.confidence,
            "frequency": self.frequency, "impact": self.impact, "status": self.status,
            "created_at": self.created_at, "tags": list(self.tags), "data": dict(self.data),
            "validation": dict(self.validation), "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "LearningItem":
        target = _KIND_CLASSES.get(d.get("kind", "item"), LearningItem)
        item = target(
            title=str(d.get("title", "")), detail=str(d.get("detail", "")),
            evidence=list(d.get("evidence", []) or []),
            confidence=float(d.get("confidence", 0.0)), frequency=int(d.get("frequency", 0)),
            impact=float(d.get("impact", 0.0)), status=str(d.get("status", "proposed")),
            created_at=str(d.get("created_at", "")), tags=list(d.get("tags", []) or []),
            data=dict(d.get("data", {}) or {}), validation=dict(d.get("validation", {}) or {}),
        )
        item.id = str(d.get("id", "")) or item.finalize().id
        item.hash = str(d.get("hash", "")) or item.hash
        return item


@dataclass
class LearningSignal(LearningItem):
    KIND: ClassVar[str] = "signal"


@dataclass
class LearningPattern(LearningItem):
    KIND: ClassVar[str] = "pattern"


@dataclass
class LearningLesson(LearningItem):
    KIND: ClassVar[str] = "lesson"


@dataclass
class LearningRecommendation(LearningItem):
    KIND: ClassVar[str] = "recommendation"


@dataclass
class LearningHypothesis(LearningItem):
    KIND: ClassVar[str] = "hypothesis"


_KIND_CLASSES = {
    "signal": LearningSignal, "pattern": LearningPattern, "lesson": LearningLesson,
    "recommendation": LearningRecommendation, "hypothesis": LearningHypothesis,
    "item": LearningItem,
}


__all__ = [
    "LearningKind", "LearningStatus", "can_transition",
    "LearningItem", "LearningSignal", "LearningPattern", "LearningLesson",
    "LearningRecommendation", "LearningHypothesis",
]
