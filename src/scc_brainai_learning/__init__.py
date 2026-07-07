"""SCC BrainAI Learning — couche officielle d'apprentissage de BrainAI.

Transforme l'**expérience** conservée par BrainAI Memory (11) en **apprentissages
exploitables** : signaux, patterns, leçons, recommandations et hypothèses. Lecture
seule de la mémoire (interface publique) ; aucune autre couche n'est modifiée.

Garde-fous : **aucun apprentissage autonome dangereux**, **aucune auto-modification**
de doctrine, workflow, agent, mémoire, graphe ou code. Tout apprentissage est une
**proposition traçable, vérifiable et révocable**, soumise à **validation humaine**.
Déterministe, stdlib pur, sans réseau.
"""

from __future__ import annotations

__version__ = "1.0.0"

from scc_brainai_learning.core.config import LearningConfig, load_config
from scc_brainai_learning.core.model import (
    LearningHypothesis,
    LearningItem,
    LearningLesson,
    LearningPattern,
    LearningRecommendation,
    LearningSignal,
    LearningStatus,
)
from scc_brainai_learning.engine import LearningEngine
from scc_brainai_learning.index import LearningIndex
from scc_brainai_learning.validation import HumanValidationPolicy

__all__ = [
    "__version__",
    "LearningEngine",
    "LearningConfig",
    "load_config",
    "LearningItem",
    "LearningSignal",
    "LearningPattern",
    "LearningLesson",
    "LearningRecommendation",
    "LearningHypothesis",
    "LearningStatus",
    "LearningIndex",
    "HumanValidationPolicy",
]
