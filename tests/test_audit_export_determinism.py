"""Tests d'audit, d'export, de rapport et de déterminisme."""

from __future__ import annotations

import json

from scc_brainai_learning.core.config import LearningConfig
from scc_brainai_learning.engine import LearningEngine
from scc_brainai_learning.sources.memory_source import MemorySource


def test_audit_ok(engine):
    a = engine.audit()
    assert a["ok"] is True
    assert a["integrity"]["ok"] is True
    assert a["traceability"]["ok"] is True


def test_integrity_detects_tampering(engine):
    it = engine.items[0]
    it.detail = "TAMPERED"       # altération directe sans re-finalize
    a = engine.audit()
    assert a["integrity"]["ok"] is False
    assert it.id in a["integrity"]["broken"]


def test_traceability_detects_dangling(engine):
    it = engine.items[0]
    it.evidence = ["mem_does_not_exist"]
    a = engine.audit()
    assert a["traceability"]["ok"] is False


def test_export_json_and_markdown(engine, tmp_path):
    data = engine.export_dict()
    assert data["counts"]["recommendation"] > 0
    md = engine.export_markdown()
    assert "# BrainAI Learning" in md
    jp = engine.export_json(tmp_path / "l.json")
    assert jp.exists()


def test_report_shape(engine):
    r = engine.report()
    assert r["audit"]["safety"] is True
    assert r["top_recommendations"]
    assert "propositions" in r["safety_note"]


def test_self_check(engine):
    sc = engine.self_check()
    assert sc["ok"] is True
    labels = {c["label"] for c in sc["checks"]}
    assert {"safety_no_autoapply", "traceability", "no_llm_no_network"} <= labels


def test_deterministic_analysis(config, memory_store):
    def run():
        cfg = LearningConfig(data_dir=config.data_dir.parent / f"l_{id(object())}")
        eng = LearningEngine(config=cfg, memory_source=MemorySource(cfg, store=memory_store))
        eng.analyze()
        # ignore la persistance : compare le contenu des apprentissages
        return json.dumps([it.to_dict() for it in eng.items], sort_keys=True, ensure_ascii=False)
    assert run() == run()


def test_idempotent_reanalyze(engine):
    before = {it.id for it in engine.items}
    engine.analyze()
    after = {it.id for it in engine.items}
    assert before == after   # mêmes ids (dérivés du contenu) : pas de doublon
