"""Analyse de la mémoire BrainAI → **signaux** d'apprentissage.

Détecteurs déterministes et purs, appliqués aux entrées de mémoire (lecture
seule). Chaque signal est **tracé** vers les événements mémoire sources (evidence)
et **scoré** (confiance/fréquence/impact). Aucun signal n'est appliqué : ce sont
des observations propositionnelles.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List

from scc_brainai_learning.core.config import LearningConfig
from scc_brainai_learning.core.model import LearningSignal
from scc_brainai_learning.scoring import confidence, impact


def _mk_signal(title: str, detail: str, evidence: List[str], frequency: int,
               total: int, category: str, config: LearningConfig,
               extra: Dict[str, Any] = None) -> LearningSignal:
    sig = LearningSignal(
        title=title, detail=detail, evidence=sorted(set(evidence)), frequency=frequency,
        confidence=confidence(frequency, frequency, total, config.strong_frequency),
        impact=impact(category), created_at=config.as_of,
        tags=["signal", category], data={"category": category, **(extra or {})},
    )
    return sig.finalize()


def detect_signals(entries: List[Dict[str, Any]], config: LearningConfig) -> List[LearningSignal]:
    by_subtype: Dict[str, List[dict]] = defaultdict(list)
    for e in entries:
        if e.get("kind") == "event":
            by_subtype[e.get("subtype", "")].append(e)

    cycles = max(len(by_subtype.get("request", [])), 1)
    signals: List[LearningSignal] = []
    minf = config.min_frequency

    # 2 & 5. Intentions récurrentes (proxy de workflows fréquents).
    intents: Dict[str, List[str]] = defaultdict(list)
    for e in by_subtype.get("intent", []):
        intents[str(e["data"].get("intent", ""))].append(e["id"])
    for intent, ids in sorted(intents.items()):
        if intent and len(ids) >= minf:
            signals.append(_mk_signal(
                f"Intention récurrente : {intent}",
                f"L'intention « {intent} » apparaît {len(ids)} fois sur {cycles} cycle(s).",
                ids, len(ids), cycles, "intent_recurrence", config, {"intent": intent}))

    # 5. Workflows fréquents (signatures d'actions de plan).
    plans: Dict[str, List[str]] = defaultdict(list)
    for e in by_subtype.get("plan", []):
        actions = tuple(sorted(e["data"].get("actions", []) or []))
        plans[",".join(actions)].append(e["id"])
    for sig_key, ids in sorted(plans.items()):
        if sig_key and len(ids) >= minf:
            signals.append(_mk_signal(
                f"Workflow fréquent : [{sig_key}]",
                f"La séquence d'actions [{sig_key}] revient {len(ids)} fois.",
                ids, len(ids), cycles, "workflow_frequency", config, {"actions": sig_key.split(",")}))

    # 6. Agents fréquemment mobilisés.
    agents: Dict[str, List[str]] = defaultdict(list)
    for e in by_subtype.get("agents", []):
        for aid in e["data"].get("agents", []) or []:
            agents[aid].append(e["id"])
    for aid, ids in sorted(agents.items()):
        if len(ids) >= minf:
            ubiquitous = len(ids) >= cycles
            signals.append(_mk_signal(
                f"Agent fréquemment mobilisé : {aid}",
                f"L'agent {aid} est mobilisé dans {len(ids)}/{cycles} cycle(s)"
                + (" (systématique)." if ubiquitous else "."),
                ids, len(ids), cycles, "agent_mobilization", config,
                {"agent": aid, "ubiquitous": ubiquitous}))

    # 3. Erreurs récurrentes.
    errors: Dict[str, List[str]] = defaultdict(list)
    for e in by_subtype.get("error", []):
        key = str(e["data"].get("error") or e["data"].get("runtime_status") or "unknown")
        errors[key].append(e["id"])
    for key, ids in sorted(errors.items()):
        if len(ids) >= minf:
            signals.append(_mk_signal(
                f"Erreur récurrente : {key}",
                f"L'erreur « {key} » survient {len(ids)} fois.",
                ids, len(ids), cycles, "error_recurrence", config, {"error": key}))

    # 4. Préférences stables (même clé/valeur répétée) et conflits.
    prefs: Dict[str, List[str]] = defaultdict(list)
    pref_values: Dict[str, set] = defaultdict(set)
    for e in entries:
        if e.get("kind") == "preference":
            k = str(e["data"].get("key", ""))
            v = e["data"].get("value")
            prefs[k].append(e["id"])
            pref_values[k].add(repr(v))
    for k, ids in sorted(prefs.items()):
        if k and len(pref_values[k]) == 1 and len(ids) >= minf:
            signals.append(_mk_signal(
                f"Préférence stable : {k}",
                f"La préférence « {k} » est constante sur {len(ids)} occurrence(s).",
                ids, len(ids), cycles, "preference_stability", config, {"key": k}))
        elif k and len(pref_values[k]) > 1:
            signals.append(_mk_signal(
                f"Préférence instable : {k}",
                f"La préférence « {k} » prend {len(pref_values[k])} valeurs différentes.",
                ids, len(ids), cycles, "preference_conflict", config, {"key": k}))

    # 7. Lacunes / zones faibles.
    n_errors = len(by_subtype.get("error", []))
    if n_errors and cycles:
        rate = round(n_errors / cycles, 3)
        signals.append(_mk_signal(
            "Zone faible : taux d'erreur",
            f"{n_errors} erreur(s) sur {cycles} cycle(s) (taux {rate}).",
            [e["id"] for e in by_subtype.get("error", [])], n_errors, cycles,
            "weak_zone", config, {"error_rate": rate}))
    if len({str(e["data"].get("intent", "")) for e in by_subtype.get("intent", [])}) == 1 and cycles >= config.strong_frequency:
        ids = [e["id"] for e in by_subtype.get("intent", [])]
        signals.append(_mk_signal(
            "Zone faible : faible diversité d'intentions",
            "Une seule intention est utilisée malgré de nombreux cycles.",
            ids, cycles, cycles, "weak_zone", config, {"diversity": "low"}))

    return sorted(signals, key=lambda s: s.id)


__all__ = ["detect_signals"]
