"""Tests des détecteurs, du regroupement et de la synthèse."""

from __future__ import annotations


def test_analyze_produces_all_kinds(engine):
    kinds = engine.index.counts()
    for k in ("signal", "pattern", "lesson", "recommendation", "hypothesis"):
        assert kinds.get(k, 0) > 0, f"aucun apprentissage de genre {k}"


def test_recurring_intent_detected(engine):
    sigs = engine.search(kind="signal", text="intention récurrente")
    intents = {s["data"].get("intent") for s in sigs}
    assert "governance" in intents


def test_recurring_error_detected(engine):
    errs = engine.search(kind="signal", tag="error_recurrence")
    assert errs
    assert any("boom" in s["data"].get("error", "") for s in errs)


def test_frequent_agent_detected(engine):
    ag = engine.search(kind="signal", tag="agent_mobilization")
    agents = {s["data"].get("agent") for s in ag}
    assert "SCC-AGENT-0020" in agents  # superviseur, mobilisé partout
    # le superviseur est ubiquitaire
    sup = next(s for s in ag if s["data"].get("agent") == "SCC-AGENT-0020")
    assert sup["data"]["ubiquitous"] is True


def test_stable_preference_detected(engine):
    prefs = engine.search(kind="signal", tag="preference_stability")
    assert any(s["data"].get("key") == "langue" for s in prefs)


def test_weak_zone_error_rate(engine):
    weak = engine.search(kind="signal", tag="weak_zone")
    assert any("error_rate" in s["data"] for s in weak)


def test_scoring_bounds(engine):
    for it in engine.items:
        assert 0.0 <= it.confidence <= 1.0
        assert 0.0 <= it.impact <= 1.0
        assert it.frequency >= 0


def test_traceability_evidence(engine):
    # chaque apprentissage cite au moins une entrée mémoire existante
    mem_ids = {e["id"] for e in engine.source.entries()}
    for it in engine.items:
        assert it.evidence
        assert all(eid in mem_ids for eid in it.evidence)
