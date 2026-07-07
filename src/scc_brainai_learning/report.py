"""LearningReport — synthèse déterministe des apprentissages proposés."""

from __future__ import annotations

from typing import Any, Dict, List


def learning_report(engine) -> Dict[str, Any]:
    items = engine.items
    by_kind: Dict[str, int] = {}
    by_status: Dict[str, int] = {}
    for it in items:
        by_kind[it.kind] = by_kind.get(it.kind, 0) + 1
        by_status[it.status] = by_status.get(it.status, 0) + 1
    audit = engine.audit()
    # Recommandations les mieux notées (impact × confiance), déterministe.
    recos = [it for it in items if it.kind == "recommendation"]
    ranked = sorted(recos, key=lambda it: (-round(it.impact * it.confidence, 4), it.id))
    return {
        "as_of": engine.config.as_of,
        "totals": {"items": len(items)},
        "by_kind": dict(sorted(by_kind.items())),
        "by_status": dict(sorted(by_status.items())),
        "top_recommendations": [
            {"id": it.id, "title": it.title, "confidence": it.confidence,
             "impact": it.impact, "status": it.status} for it in ranked[:5]],
        "audit": {"ok": audit["ok"], "integrity": audit["integrity"]["ok"],
                  "traceability": audit["traceability"]["ok"], "safety": audit["safety"]["ok"]},
        "safety_note": "Tous les apprentissages sont des propositions ; aucune application automatique.",
    }


def render_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = [
        "# BrainAI Learning — rapport d'apprentissage",
        "",
        f"> Instantané déterministe — `as_of` : {report.get('as_of')}",
        "",
        f"**{report['totals']['items']} apprentissage(s)** — tous **propositionnels** "
        "(aucune application automatique).",
        "",
        "## Répartition par genre",
        "",
        "| Genre | Nombre |",
        "|-------|--------|",
    ]
    for k, v in report["by_kind"].items():
        lines.append(f"| {k} | {v} |")
    lines += ["", "## Répartition par statut", "", "| Statut | Nombre |", "|--------|--------|"]
    for k, v in report["by_status"].items():
        lines.append(f"| {k} | {v} |")
    lines += ["", "## Recommandations les mieux notées (proposées)", ""]
    for r in report["top_recommendations"]:
        lines.append(f"- `{r['status']}` **{r['title']}** — confiance {r['confidence']}, impact {r['impact']}")
    lines += [
        "", "## Audit", "",
        f"- intégrité : {report['audit']['integrity']} · traçabilité : {report['audit']['traceability']} · "
        f"sûreté : {report['audit']['safety']}",
        "",
        f"> {report['safety_note']}",
        "",
        "*Rapport généré par BrainAI Learning — déterministe, sans réseau ni LLM.*",
    ]
    return "\n".join(lines) + "\n"


__all__ = ["learning_report", "render_markdown"]
