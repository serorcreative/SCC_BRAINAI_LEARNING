"""Audit de la couche d'apprentissage : intégrité, traçabilité, sûreté.

Trois contrôles :

* **intégrité** : l'empreinte de chaque apprentissage correspond à son contenu ;
* **traçabilité** : chaque preuve (evidence) pointe vers un événement mémoire réel ;
* **sûreté** : tout apprentissage non « proposé » porte un approbateur **humain**
  (aucune auto-validation) et aucun n'est marqué comme « appliqué ».
"""

from __future__ import annotations

from typing import Any, Dict, List, Set

from scc_brainai_learning.core.model import LearningItem, LearningStatus


def verify_integrity(items: List[LearningItem]) -> Dict[str, Any]:
    broken = sorted(it.id for it in items if not it.verify())
    return {"ok": not broken, "broken": broken}


def verify_traceability(items: List[LearningItem], memory_ids: Set[str]) -> Dict[str, Any]:
    dangling: List[str] = []
    for it in items:
        for eid in it.evidence:
            if eid not in memory_ids:
                dangling.append(f"{it.id}->{eid}")
    return {"ok": not dangling, "dangling": sorted(dangling)}


def verify_safety(items: List[LearningItem]) -> Dict[str, Any]:
    auto_changed: List[str] = []
    applied: List[str] = []
    for it in items:
        # tout état != proposed doit résulter d'une action humaine tracée
        if it.status != LearningStatus.PROPOSED.value:
            if not it.validation.get("approver"):
                auto_changed.append(it.id)
        # aucun apprentissage ne doit être marqué « appliqué »
        if it.data.get("applied") is True:
            applied.append(it.id)
    return {"ok": not auto_changed and not applied,
            "auto_changed_without_human": sorted(auto_changed),
            "applied": sorted(applied)}


def audit_report(items: List[LearningItem], memory_ids: Set[str]) -> Dict[str, Any]:
    integrity = verify_integrity(items)
    traceability = verify_traceability(items, memory_ids)
    safety = verify_safety(items)
    return {
        "ok": integrity["ok"] and traceability["ok"] and safety["ok"],
        "integrity": integrity, "traceability": traceability, "safety": safety,
        "items": len(items),
    }


__all__ = ["verify_integrity", "verify_traceability", "verify_safety", "audit_report"]
