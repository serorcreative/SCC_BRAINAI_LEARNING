"""LearningIndex — index de recherche des apprentissages (déterministe)."""

from __future__ import annotations

from typing import Dict, List, Optional

from scc_brainai_learning.core.clock import canonical
from scc_brainai_learning.core.model import LearningItem


class LearningIndex:
    def __init__(self) -> None:
        self._by_id: Dict[str, LearningItem] = {}
        self._text: Dict[str, str] = {}

    def add(self, item: LearningItem) -> None:
        self._by_id[item.id] = item
        blob = f"{item.kind} {item.title} {item.detail} {' '.join(item.tags)} {canonical(item.data)}"
        self._text[item.id] = blob.lower()

    def rebuild(self, items: List[LearningItem]) -> None:
        self._by_id.clear()
        self._text.clear()
        for it in items:
            self.add(it)

    def get(self, item_id: str) -> Optional[LearningItem]:
        return self._by_id.get(item_id)

    def search(self, *, kind: Optional[str] = None, status: Optional[str] = None,
               tag: Optional[str] = None, text: Optional[str] = None,
               min_confidence: float = 0.0, limit: int = 100) -> List[LearningItem]:
        q = (text or "").strip().lower()
        out: List[LearningItem] = []
        for iid in sorted(self._by_id):
            it = self._by_id[iid]
            if kind and it.kind != kind:
                continue
            if status and it.status != status:
                continue
            if tag and tag not in it.tags:
                continue
            if it.confidence < min_confidence:
                continue
            if q and q not in self._text.get(iid, ""):
                continue
            out.append(it)
        if limit and limit > 0:
            out = out[:limit]
        return out

    def counts(self) -> Dict[str, int]:
        by_kind: Dict[str, int] = {}
        for it in self._by_id.values():
            by_kind[it.kind] = by_kind.get(it.kind, 0) + 1
        return dict(sorted(by_kind.items()))

    def all(self) -> List[LearningItem]:
        return [self._by_id[k] for k in sorted(self._by_id)]

    def __len__(self) -> int:
        return len(self._by_id)


__all__ = ["LearningIndex"]
