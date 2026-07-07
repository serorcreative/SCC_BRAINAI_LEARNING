"""CLI de la couche d'apprentissage BrainAI (``scc-brain-learning``).

Analyse, consultation, **validation humaine**, export, audit. Sortie JSON
déterministe. Aucune commande n'applique un apprentissage : seule la validation
humaine change un statut, et cela ne modifie **aucune** autre couche.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, List, Optional

from scc_brainai_learning import __version__
from scc_brainai_learning.core.config import load_config
from scc_brainai_learning.core.errors import LearningError
from scc_brainai_learning.engine import LearningEngine


def _out(obj: Any) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def _engine(args) -> LearningEngine:
    return LearningEngine(config=load_config(args.config))


def cmd_analyze(args) -> int:
    _out(_engine(args).analyze()); return 0


def cmd_learnings(args) -> int:
    eng = _engine(args)
    _out(eng.search(kind=args.kind, status=args.status, tag=args.tag, text=args.text,
                    min_confidence=float(args.min_confidence), limit=int(args.limit)))
    return 0


def cmd_get(args) -> int:
    try:
        _out(_engine(args).get(args.id)); return 0
    except LearningError as exc:
        _out({"error": str(exc)}); return 1


def _transition(args, action: str) -> int:
    try:
        _out(getattr(_engine(args), action)(args.id, args.by, args.reason)); return 0
    except LearningError as exc:
        _out({"error": str(exc)}); return 1


def cmd_report(args) -> int:
    _out(_engine(args).report()); return 0


def cmd_audit(args) -> int:
    a = _engine(args).audit(); _out(a); return 0 if a["ok"] else 1


def cmd_self_check(args) -> int:
    sc = _engine(args).self_check(); _out(sc); return 0 if sc["ok"] else 1


def cmd_export(args) -> int:
    eng = _engine(args)
    if args.format == "json":
        out = eng.export_json(Path(args.out) if args.out else None)
    else:
        out = eng.export_markdown(Path(args.out) if args.out else None)
    if args.out:
        _out({"exported": str(out)})
    else:
        print(out if isinstance(out, str) else json.dumps(out, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="scc-brain-learning",
                                     description="Couche d'apprentissage de BrainAI (propositions traçables).")
    parser.add_argument("--version", action="version", version=f"scc-brain-learning {__version__}")
    parser.add_argument("--config", type=Path, default=None)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("analyze", help="Analyse la mémoire et produit des propositions.").set_defaults(func=cmd_analyze)
    sub.add_parser("report", help="Rapport d'apprentissage.").set_defaults(func=cmd_report)
    sub.add_parser("audit", help="Audit (intégrité, traçabilité, sûreté).").set_defaults(func=cmd_audit)
    sub.add_parser("self-check", help="Auto-vérification.").set_defaults(func=cmd_self_check)

    p_l = sub.add_parser("learnings", help="Liste/recherche des apprentissages.")
    for opt in ("kind", "status", "tag", "text"):
        p_l.add_argument(f"--{opt}", default=None)
    p_l.add_argument("--min-confidence", default="0")
    p_l.add_argument("--limit", default="100")
    p_l.set_defaults(func=cmd_learnings)

    p_get = sub.add_parser("get", help="Détail d'un apprentissage.")
    p_get.add_argument("id"); p_get.set_defaults(func=cmd_get)

    for action in ("validate", "reject", "revoke"):
        p = sub.add_parser(action, help=f"{action} (validation humaine) un apprentissage.")
        p.add_argument("id")
        p.add_argument("--by", required=True, help="approbateur humain")
        p.add_argument("--reason", default="")
        p.set_defaults(func=lambda a, _act=action: _transition(a, _act))

    p_exp = sub.add_parser("export", help="Exporte les apprentissages (JSON/Markdown).")
    p_exp.add_argument("--format", choices=["json", "md"], default="json")
    p_exp.add_argument("--out", default=None)
    p_exp.set_defaults(func=cmd_export)
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


__all__ = ["main", "build_parser"]
