"""Tests de la CLI d'apprentissage."""

from __future__ import annotations

import json

import pytest

from scc_brainai_learning.cli import main


@pytest.fixture
def cfg_file(config, memory_store, tmp_path):
    # matérialise le registre via une analyse, puis écrit une config pointant dessus
    from scc_brainai_learning.engine import LearningEngine
    from scc_brainai_learning.sources.memory_source import MemorySource
    LearningEngine(config=config, memory_source=MemorySource(config, store=memory_store)).analyze()
    path = tmp_path / "learning.json"
    path.write_text(json.dumps({
        "paths": {"data_dir": str(config.data_dir)},
        "as_of": config.as_of,
        "extra": {"memory_data_dir": str(memory_store.config.data_dir)},
    }), encoding="utf-8")
    return path


def _run(argv, cfg_file, capsys):
    rc = main(["--config", str(cfg_file)] + argv)
    return rc, capsys.readouterr().out


def test_cli_report(cfg_file, capsys):
    rc, out = _run(["report"], cfg_file, capsys)
    data = json.loads(out)
    assert rc == 0
    assert data["audit"]["safety"] is True


def test_cli_learnings_filter(cfg_file, capsys):
    rc, out = _run(["learnings", "--kind", "recommendation"], cfg_file, capsys)
    data = json.loads(out)
    assert rc == 0
    assert all(it["kind"] == "recommendation" for it in data)


def test_cli_validate_flow(cfg_file, capsys):
    _, out = _run(["learnings", "--kind", "recommendation"], cfg_file, capsys)
    rid = json.loads(out)[0]["id"]
    rc, out = _run(["validate", rid, "--by", "frederique", "--reason", "utile"], cfg_file, capsys)
    assert rc == 0
    assert json.loads(out)["status"] == "validated"


def test_cli_validate_requires_by(cfg_file, capsys):
    # --by est requis : argparse renvoie un code d'erreur (SystemExit)
    with pytest.raises(SystemExit):
        main(["--config", str(cfg_file), "validate", "x"])


def test_cli_audit(cfg_file, capsys):
    rc, out = _run(["audit"], cfg_file, capsys)
    assert rc == 0
    assert json.loads(out)["ok"] is True
