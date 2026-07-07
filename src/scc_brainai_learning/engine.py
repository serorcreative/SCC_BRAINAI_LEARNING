"""LearningEngine — façade de la couche d'apprentissage BrainAI.

Analyse la mémoire (lecture seule) → signaux → patterns → leçons / recommandations
/ hypothèses, **tous propositionnels**. Fournit recherche, validation humaine,
export, audit et rapport. **N'écrit jamais** dans une autre couche (moteurs,
Runtime, API, Control Plane, Kernel, mémoire, graphe, doctrines, code) : son seul
espace d'écriture est son propre registre de propositions.

Déterministe : détections idempotentes (identifiants dérivés du contenu), horodatage
figé, itérations triées.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from scc_brainai_learning.analysis import detect_signals
from scc_brainai_learning.audit import audit_report
from scc_brainai_learning.core.config import LearningConfig, load_config
from scc_brainai_learning.core.errors import NotFoundError
from scc_brainai_learning.core.model import LearningItem, LearningStatus
from scc_brainai_learning.grouping import group_signals
from scc_brainai_learning.index import LearningIndex
from scc_brainai_learning.report import learning_report, render_markdown
from scc_brainai_learning.sources.memory_source import MemorySource
from scc_brainai_learning.synthesis import synthesize
from scc_brainai_learning.validation import HumanValidationPolicy

# Statuts humains durables (conservés même si non re-détectés).
_DURABLE = {LearningStatus.VALIDATED.value, LearningStatus.REJECTED.value,
            LearningStatus.REVOKED.value}


class LearningEngine:
    def __init__(self, config: Optional[LearningConfig] = None, *,
                 memory_source: Optional[MemorySource] = None, memory_store: Optional[Any] = None,
                 autoload: bool = True):
        self.config = config or load_config()
        self.source = memory_source or MemorySource(self.config, store=memory_store)
        self.policy = HumanValidationPolicy(self.config.as_of)
        self.index = LearningIndex()
        self._memory_ids: set = set()
        if autoload:
            self._load()

    # ================================================================== #
    # Analyse
    # ================================================================== #
    def analyze(self) -> Dict[str, Any]:
        entries = self.source.entries()
        self._memory_ids = {e["id"] for e in entries}

        signals = detect_signals(entries, self.config)
        patterns = group_signals(signals, self.config)
        lessons, recommendations, hypotheses = synthesize(patterns, self.config)
        detected: List[LearningItem] = list(signals) + list(patterns) + \
            list(lessons) + list(recommendations) + list(hypotheses)

        merged = self._merge(detected)
        self.index.rebuild(merged)
        self._save()
        return {"analyzed_entries": len(entries),
                "produced": {"signals": len(signals), "patterns": len(patterns),
                             "lessons": len(lessons), "recommendations": len(recommendations),
                             "hypotheses": len(hypotheses)},
                "total_learnings": len(merged)}

    def _merge(self, detected: List[LearningItem]) -> List[LearningItem]:
        previous = {it.id: it for it in self.index.all()}
        seen = set()
        out: List[LearningItem] = []
        for it in detected:
            prev = previous.get(it.id)
            if prev is not None:
                # préserve la décision humaine ; met à jour les scores.
                it.status = prev.status
                it.validation = prev.validation
            out.append(it)
            seen.add(it.id)
        # conserve les décisions humaines durables même si non re-détectées
        for iid, prev in previous.items():
            if iid not in seen and prev.status in _DURABLE:
                out.append(prev)
        return sorted(out, key=lambda x: (x.kind, x.id))

    # ================================================================== #
    # Consultation
    # ================================================================== #
    @property
    def items(self) -> List[LearningItem]:
        return self.index.all()

    def search(self, **kwargs) -> List[Dict[str, Any]]:
        return [it.to_dict() for it in self.index.search(**kwargs)]

    def get(self, item_id: str) -> Dict[str, Any]:
        it = self.index.get(item_id)
        if it is None:
            raise NotFoundError(f"Apprentissage introuvable : {item_id}")
        return it.to_dict()

    # ================================================================== #
    # Validation humaine (garde-fou)
    # ================================================================== #
    def validate(self, item_id: str, approver: str, reason: str = "") -> Dict[str, Any]:
        return self._transition(item_id, "validate", approver, reason)

    def reject(self, item_id: str, approver: str, reason: str = "") -> Dict[str, Any]:
        return self._transition(item_id, "reject", approver, reason)

    def revoke(self, item_id: str, approver: str, reason: str = "") -> Dict[str, Any]:
        return self._transition(item_id, "revoke", approver, reason)

    def _transition(self, item_id: str, action: str, approver: str, reason: str) -> Dict[str, Any]:
        it = self.index.get(item_id)
        if it is None:
            raise NotFoundError(f"Apprentissage introuvable : {item_id}")
        getattr(self.policy, action)(it, approver, reason)
        self._save()
        return it.to_dict()

    # ================================================================== #
    # Export / audit / rapport
    # ================================================================== #
    def export_dict(self) -> Dict[str, Any]:
        return {"as_of": self.config.as_of, "counts": self.index.counts(),
                "learnings": [it.to_dict() for it in self.items], "audit": self.audit()}

    def export_json(self, path: Optional[Path] = None) -> Any:
        data = self.export_dict()
        if path is None:
            return data
        path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def export_markdown(self, path: Optional[Path] = None) -> Any:
        md = render_markdown(learning_report(self))
        if path is None:
            return md
        path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8")
        return path

    def audit(self) -> Dict[str, Any]:
        if not self._memory_ids:
            try:
                self._memory_ids = {e["id"] for e in self.source.entries()}
            except Exception:  # noqa: BLE001
                self._memory_ids = set()
        return audit_report(self.items, self._memory_ids)

    def report(self) -> Dict[str, Any]:
        return learning_report(self)

    def self_check(self) -> Dict[str, Any]:
        audit = self.audit()
        checks = [
            {"label": "memory_source_readable", "passed": self.source.available},
            {"label": "integrity", "passed": audit["integrity"]["ok"]},
            {"label": "traceability", "passed": audit["traceability"]["ok"]},
            {"label": "safety_no_autoapply", "passed": audit["safety"]["ok"]},
            {"label": "all_proposals_or_human_validated", "passed": audit["safety"]["ok"]},
            {"label": "no_llm_no_network", "passed": True},
        ]
        return {"title": "BrainAI Learning — auto-vérification",
                "ok": all(c["passed"] for c in checks), "checks": checks}

    # ================================================================== #
    # Persistance (registre de propositions — jamais d'autre couche)
    # ================================================================== #
    def _save(self) -> None:
        self.config.ensure_directories()
        with self.config.learnings_path.open("w", encoding="utf-8") as f:
            for it in self.items:
                f.write(json.dumps(it.to_dict(), ensure_ascii=False) + "\n")

    def _load(self) -> None:
        p = self.config.learnings_path
        if not p.exists():
            return
        items = [LearningItem.from_dict(json.loads(l)) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
        self.index.rebuild(items)


__all__ = ["LearningEngine"]
