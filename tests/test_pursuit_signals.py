"""L5 — raccord des expériences de Pursuit (subtype 'pursuit_delivered', raccord L3) à Learning-12.

CONNECTER, PAS RECONSTRUIRE : ``pursuit_delivered`` est traduit en signaux ÉLÉMENTAIRES natifs
(``category='pursuit_delivery'``), gaté par ``min_frequency`` sur le TOTAL transverse ; la consolidation
multi-Pursuits est déléguée au ``group_signals`` natif ; confidence/impact/synthesis existants réutilisés.
Aucune auto-application ; tout reste ``proposed`` jusqu'à validation humaine ; Memory-11 reste read-only.
"""

from __future__ import annotations

import pytest

from scc_brainai_learning.core.config import LearningConfig
from scc_brainai_learning.core.errors import ValidationError
from scc_brainai_learning.engine import LearningEngine
from scc_brainai_learning.sources.memory_source import MemorySource

# La mémoire BrainAI (11) est rendue importable par conftest.py.


def _store(tmp_path):
    from scc_brainai_memory import BrainMemoryStore, MemoryConfig
    return BrainMemoryStore(config=MemoryConfig(data_dir=tmp_path / "mem"))


def _deliver(store, ref, *, project="site", result="obj", status="delivered"):
    data = {"pursuit_ref": ref, "pursuit_id": ref, "need": "n", "status": status,
            "project": project, "result": result, "provenance_ids": {"build_id": "b"}, "as_of": "t0"}
    if project is None:
        data.pop("project")
    return store.record_event("pursuit_delivered", data,
                              tags=["jalon2", "delivered", "pursuit", f"pursuit:{ref}"])


def _engine(tmp_path, store):
    config = LearningConfig(data_dir=tmp_path / "learn")
    eng = LearningEngine(config=config, memory_source=MemorySource(config, store=store))
    eng.analyze()
    return eng


def test_below_min_frequency_no_pursuit_learning(tmp_path):
    """< min_frequency livraisons → aucun signal/pattern/lesson Pursuit (anti-dilution)."""
    store = _store(tmp_path)
    _deliver(store, "pursuit_a")                       # une seule (min_frequency par défaut = 2)
    eng = _engine(tmp_path, store)
    assert eng.search(tag="pursuit_delivery") == []    # ni signal, ni pattern, ni leçon


def test_recurring_deliveries_produce_proposed_elementary_signals(tmp_path):
    """Seuil atteint → un signal ÉLÉMENTAIRE proposé par livraison ; evidence = IDs Memory-11 réels ;
    plusieurs pursuit_ref distincts conservés dans les signaux sources."""
    store = _store(tmp_path)
    ids = [_deliver(store, r).id for r in ("pursuit_a", "pursuit_b", "pursuit_c")]
    eng = _engine(tmp_path, store)
    sigs = eng.search(kind="signal", tag="pursuit_delivery")
    assert len(sigs) == 3
    assert all(s["status"] == "proposed" for s in sigs)
    assert {e for s in sigs for e in s["evidence"]} == set(ids)          # IDs Memory-11 réels
    assert {s["data"].get("pursuit_ref") for s in sigs} == {"pursuit_a", "pursuit_b", "pursuit_c"}


def test_native_consolidation_single_transverse_pattern(tmp_path):
    """group_signals natif : plusieurs Pursuits de projects DIFFÉRENTS → UN seul pattern transverse
    (par catégorie, pas par project), evidence = union des IDs."""
    store = _store(tmp_path)
    ids = [_deliver(store, r, project=p).id
           for r, p in [("pursuit_a", "site"), ("pursuit_b", "api"), ("pursuit_c", "site")]]
    eng = _engine(tmp_path, store)
    pats = eng.search(kind="pattern", tag="pursuit_delivery")
    assert len(pats) == 1                                                # transverse, non regroupé par project
    assert set(pats[0]["evidence"]) == set(ids)                          # union multi-Pursuits
    assert pats[0]["frequency"] == 3                                     # somme native


def test_no_project_bucket_no_question_mark(tmp_path):
    """project absent → aucune donnée « ? » fabriquée ; consolidation par catégorie native uniquement."""
    store = _store(tmp_path)
    for r in ("pursuit_a", "pursuit_b"):
        _deliver(store, r, project=None)
    eng = _engine(tmp_path, store)
    sigs = eng.search(kind="signal", tag="pursuit_delivery")
    assert len(sigs) == 2
    for s in sigs:
        assert s["data"].get("project") in (None, "")                   # jamais "?"
    assert len(eng.search(kind="pattern", tag="pursuit_delivery")) == 1


def test_synthesis_only_proposed_and_native_scoring(tmp_path):
    """Récurrence → leçon + recommandation PROPOSÉES uniquement ; confidence/impact natifs ; reco non appliquée."""
    store = _store(tmp_path)
    for r in ("pursuit_a", "pursuit_b"):
        _deliver(store, r)
    eng = _engine(tmp_path, store)
    lessons = eng.search(kind="lesson", tag="pursuit_delivery")
    recos = eng.search(kind="recommendation", tag="pursuit_delivery")
    assert lessons and recos
    assert all(it["status"] == "proposed" for it in lessons + recos)
    assert all(0.0 <= it["confidence"] <= 1.0 and 0.0 <= it["impact"] <= 1.0 for it in lessons + recos)
    assert all(it["data"].get("applied") is False for it in recos)      # jamais appliqué


def test_human_validation_required_and_not_applied(tmp_path):
    """validation exige un approbateur humain (ValidationError sinon) ; validated ≠ applied ; audit.applied == []."""
    store = _store(tmp_path)
    for r in ("pursuit_a", "pursuit_b"):
        _deliver(store, r)
    eng = _engine(tmp_path, store)
    lesson = eng.search(kind="lesson", tag="pursuit_delivery")[0]
    with pytest.raises(ValidationError):
        eng.validate(lesson["id"], "")                                  # sans approbateur humain → garde de validation
    res = eng.validate(lesson["id"], "frederique", "pertinent")
    assert res["status"] == "validated"
    audit = eng.audit()
    assert audit["safety"]["applied"] == []
    assert audit["safety"]["auto_changed_without_human"] == []
    assert eng.get(lesson["id"])["data"].get("applied") is not True


def test_reject_revoke_and_decision_survives_reanalyze(tmp_path):
    """reject / validate / revoke sur TROIS items distincts ; les trois décisions humaines survivent à une
    ré-analyse. ``revoke`` suit la voie légale native ``proposed → validated → revoked``."""
    store = _store(tmp_path)
    for r in ("pursuit_a", "pursuit_b"):
        _deliver(store, r)
    eng = _engine(tmp_path, store)
    rejected_id = eng.search(kind="signal", tag="pursuit_delivery")[0]["id"]
    validated_id = eng.search(kind="lesson", tag="pursuit_delivery")[0]["id"]
    revoked_id = eng.search(kind="recommendation", tag="pursuit_delivery")[0]["id"]
    assert len({rejected_id, validated_id, revoked_id}) == 3            # trois items distincts

    eng.reject(rejected_id, "frederique", "hors sujet")
    eng.validate(validated_id, "frederique", "ok")
    eng.validate(revoked_id, "frederique", "adopté temporairement")     # proposed -> validated (préalable légal)
    eng.revoke(revoked_id, "frederique", "obsolète")                   # validated -> revoked

    assert eng.get(rejected_id)["status"] == "rejected"
    assert eng.get(validated_id)["status"] == "validated"
    assert eng.get(revoked_id)["status"] == "revoked"

    eng.analyze()                                                       # ré-analyse

    assert eng.get(rejected_id)["status"] == "rejected"
    assert eng.get(validated_id)["status"] == "validated"
    assert eng.get(revoked_id)["status"] == "revoked"                  # les 3 décisions humaines survivent


def test_memory11_read_only_unchanged(tmp_path):
    """L'analyse Learning-12 n'écrit RIEN dans Memory-11 (strictement read-only)."""
    store = _store(tmp_path)
    for r in ("pursuit_a", "pursuit_b"):
        _deliver(store, r)
    before = store.counts()
    _engine(tmp_path, store)
    assert store.counts() == before


def test_memory11_corruption_fail_closed(tmp_path):
    """Le chemin de lecture (autoload) que Learning-12 emprunte reste fail-closed sur corruption."""
    from scc_brainai_memory import BrainMemoryStore, MemoryConfig
    from scc_brainai_memory.core.errors import MemoryCorruption
    store = _store(tmp_path)
    for r in ("pursuit_a", "pursuit_b"):
        _deliver(store, r)
    journal = tmp_path / "mem" / "brain_memory.jsonl"
    lines = journal.read_text(encoding="utf-8").splitlines()
    assert len(lines) >= 2
    lines[0] = "{ ceci n'est pas du JSON valide"                        # corruption AU MILIEU
    journal.write_text("\n".join(lines) + "\n", encoding="utf-8")
    with pytest.raises(MemoryCorruption):
        BrainMemoryStore(config=MemoryConfig(data_dir=tmp_path / "mem"))   # autoload → fail-closed
