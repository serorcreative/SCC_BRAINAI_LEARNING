"""Source d'analyse : la mémoire BrainAI (11), en **lecture seule**.

BrainAI Learning ne relit ni ne réimplémente rien : il consomme l'interface
**publique** de ``BrainMemoryStore`` (``search`` / ``export_dict`` / ``audit``).
La mémoire est localisée dynamiquement (ajout de son ``src/`` à ``sys.path``) et
jamais modifiée. Un store peut aussi être **injecté** (tests/intégration directe).
"""

from __future__ import annotations

import importlib
import sys
from typing import Any, Dict, List, Optional

from scc_brainai_learning.core.config import LearningConfig
from scc_brainai_learning.core.errors import SourceUnavailable


class MemorySource:
    def __init__(self, config: LearningConfig, store: Optional[Any] = None):
        self._config = config
        self._store = store

    def _ensure(self):
        if self._store is not None:
            return self._store
        src = self._config.memory_src
        if not src.exists():
            raise SourceUnavailable(f"Mémoire BrainAI introuvable : {src}")
        if str(src) not in sys.path:
            sys.path.insert(0, str(src))
        try:
            mem = importlib.import_module("scc_brainai_memory")
            memcfg_mod = importlib.import_module("scc_brainai_memory.core.config")
        except ImportError as exc:  # pragma: no cover
            raise SourceUnavailable(f"Import mémoire impossible : {exc}") from exc
        cfg = memcfg_mod.MemoryConfig(data_dir=self._config.memory_data_dir)
        self._store = mem.BrainMemoryStore(config=cfg)   # lecture (autoload)
        return self._store

    @property
    def available(self) -> bool:
        try:
            self._ensure()
            return True
        except SourceUnavailable:
            return False

    # -- lectures publiques --------------------------------------------- #
    def entries(self) -> List[Dict[str, Any]]:
        """Toutes les entrées mémoire (dicts), via l'interface publique de recherche."""
        return self._ensure().search(limit=10 ** 9)

    def events(self, subtype: Optional[str] = None) -> List[Dict[str, Any]]:
        return self._ensure().search(kind="event", subtype=subtype, limit=10 ** 9)

    def by_subtype(self, subtype: str) -> List[Dict[str, Any]]:
        return self._ensure().search(subtype=subtype, limit=10 ** 9)

    def memory_audit(self) -> Dict[str, Any]:
        return self._ensure().audit()

    def counts(self) -> Dict[str, int]:
        return self._ensure().counts()


__all__ = ["MemorySource"]
