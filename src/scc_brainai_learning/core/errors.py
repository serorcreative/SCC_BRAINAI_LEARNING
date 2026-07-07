"""Hiérarchie d'exceptions de la couche d'apprentissage BrainAI."""

from __future__ import annotations


class LearningError(Exception):
    """Erreur de base de la couche d'apprentissage."""


class ConfigError(LearningError):
    """Configuration absente, illisible ou invalide."""


class SourceUnavailable(LearningError):
    """La mémoire BrainAI (source) est introuvable/importable."""


class ValidationError(LearningError):
    """Transition de validation humaine interdite."""


class NotFoundError(LearningError):
    """Apprentissage introuvable."""


__all__ = ["LearningError", "ConfigError", "SourceUnavailable", "ValidationError", "NotFoundError"]
