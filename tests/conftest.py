"""Fixtures des tests de la couche d'apprentissage.

La mémoire BrainAI est **injectée** (store réel, isolé en tmp) : les tests sont des
tests d'intégration déterministes qui n'exigent aucun bootstrap réseau.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Rend la mémoire BrainAI (11) importable pour peupler la source.
_MEM_SRC = Path(__file__).resolve().parents[2] / "11_BRAINAI_MEMORY" / "src"
if str(_MEM_SRC) not in sys.path:
    sys.path.insert(0, str(_MEM_SRC))

from scc_brainai_learning.core.config import LearningConfig       # noqa: E402
from scc_brainai_learning.engine import LearningEngine            # noqa: E402
from scc_brainai_learning.sources.memory_source import MemorySource  # noqa: E402


def _response(intent, agents, ok=True, err=None):
    return {
        "ok": ok, "as_of": "2026-07-06T00:00:00+00:00",
        "request": {"query": f"q {intent}", "actor": "brainai", "autonomy": "A3"},
        "intent": intent,
        "plan": {"intent": intent, "steps": [{"action": "inspect_health"},
                                             {"action": "observe_supervision"}]},
        "agents": [{"id": a} for a in agents],
        "governance": {"doctrines": ["SCC-DOC-0016"], "adrs": ["ADR-0003"]},
        "runtime": {"job_id": "j", "kind": "echo",
                    "status": "failed" if err else "succeeded", "trust": "T1",
                    "human_approval_required": False, "error": err or ""},
        "provider": {"selected": "deterministic"},
    }


@pytest.fixture
def memory_store(tmp_path):
    from scc_brainai_memory import BrainMemoryStore, MemoryConfig
    from scc_brainai_memory.recorder import KernelRecorder
    store = BrainMemoryStore(config=MemoryConfig(data_dir=tmp_path / "mem"))
    rec = KernelRecorder(store)
    for _ in range(5):
        rec.record_response(_response("governance", ["SCC-AGENT-0002", "SCC-AGENT-0020"]))
    for _ in range(3):
        rec.record_response(_response("inspect", ["SCC-AGENT-0015", "SCC-AGENT-0020"],
                                      ok=False, err="boom"))
    store.set_preference("langue", "fr")
    store.set_preference("langue", "fr")
    return store


@pytest.fixture
def config(tmp_path):
    return LearningConfig(data_dir=tmp_path / "learn")


@pytest.fixture
def engine(config, memory_store):
    eng = LearningEngine(config=config, memory_source=MemorySource(config, store=memory_store))
    eng.analyze()
    return eng
