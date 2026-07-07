"""Tests des garde-fous : validation humaine, sûreté, aucune auto-application."""

from __future__ import annotations

import pytest

from scc_brainai_learning.core.errors import ValidationError


def test_everything_starts_proposed(engine):
    assert all(it.status == "proposed" for it in engine.items)


def test_validate_requires_human(engine):
    rid = engine.search(kind="recommendation")[0]["id"]
    with pytest.raises(ValidationError):
        engine.validate(rid, "")   # pas d'approbateur


def test_validate_then_revoke(engine):
    rid = engine.search(kind="recommendation")[0]["id"]
    engine.validate(rid, "frederique", "utile")
    item = engine.get(rid)
    assert item["status"] == "validated"
    assert item["validation"]["approver"] == "frederique"
    engine.revoke(rid, "frederique", "obsolète")
    assert engine.get(rid)["status"] == "revoked"


def test_illegal_transition_refused(engine):
    rid = engine.search(kind="recommendation")[0]["id"]
    engine.validate(rid, "frederique")
    with pytest.raises(ValidationError):
        engine.reject(rid, "frederique")   # reject après validate interdit


def test_safety_audit_passes(engine):
    audit = engine.audit()
    assert audit["safety"]["ok"] is True
    assert audit["safety"]["applied"] == []
    assert audit["safety"]["auto_changed_without_human"] == []


def test_no_learning_marked_applied(engine):
    # garde-fou : aucun apprentissage ne porte 'applied: true'
    assert all(it.data.get("applied") is not True for it in engine.items)


def test_human_decision_survives_reanalyze(engine):
    rid = engine.search(kind="recommendation")[0]["id"]
    engine.validate(rid, "frederique", "utile")
    engine.analyze()   # ré-analyse : la décision humaine doit persister
    assert engine.get(rid)["status"] == "validated"
