"""Politique de validation humaine — garde-fou central.

**Aucun apprentissage n'est jamais appliqué automatiquement.** Tout apprentissage
naît « proposé » et ne change d'état que par une **action humaine explicite**
(valider / rejeter / révoquer), tracée (approbateur, motif, horodatage figé). Les
transitions sont gardées ; l'analyse ne peut produire que des propositions.
"""

from __future__ import annotations

from typing import Any, Dict

from scc_brainai_learning.core.errors import ValidationError
from scc_brainai_learning.core.model import LearningItem, LearningStatus, can_transition


class HumanValidationPolicy:
    def __init__(self, as_of: str):
        self._as_of = as_of

    def _apply(self, item: LearningItem, target: str, action: str,
               approver: str, reason: str) -> LearningItem:
        if not approver:
            raise ValidationError("Une action de validation exige un approbateur humain explicite.")
        if not can_transition(item.status, target):
            raise ValidationError(
                f"Transition interdite : {item.status} -> {target} (apprentissage {item.id}).")
        item.status = target
        item.validation = {"action": action, "approver": approver, "reason": reason,
                           "at": self._as_of, "previous": item.validation}
        return item

    def validate(self, item: LearningItem, approver: str, reason: str = "") -> LearningItem:
        return self._apply(item, LearningStatus.VALIDATED.value, "validate", approver, reason)

    def reject(self, item: LearningItem, approver: str, reason: str = "") -> LearningItem:
        return self._apply(item, LearningStatus.REJECTED.value, "reject", approver, reason)

    def revoke(self, item: LearningItem, approver: str, reason: str = "") -> LearningItem:
        return self._apply(item, LearningStatus.REVOKED.value, "revoke", approver, reason)


__all__ = ["HumanValidationPolicy"]
