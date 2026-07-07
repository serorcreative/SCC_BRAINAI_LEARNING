"""Noyau de la couche d'apprentissage : config, erreurs, modèle."""

from __future__ import annotations

from scc_brainai_learning.core.clock import canonical, digest, short_id
from scc_brainai_learning.core.config import LearningConfig, load_config
from scc_brainai_learning.core.errors import (
    ConfigError,
    LearningError,
    NotFoundError,
    SourceUnavailable,
    ValidationError,
)
from scc_brainai_learning.core.model import (
    LearningHypothesis,
    LearningItem,
    LearningKind,
    LearningLesson,
    LearningPattern,
    LearningRecommendation,
    LearningSignal,
    LearningStatus,
    can_transition,
)

__all__ = [
    "canonical", "digest", "short_id",
    "LearningConfig", "load_config",
    "LearningError", "ConfigError", "SourceUnavailable", "ValidationError", "NotFoundError",
    "LearningKind", "LearningStatus", "can_transition",
    "LearningItem", "LearningSignal", "LearningPattern", "LearningLesson",
    "LearningRecommendation", "LearningHypothesis",
]
