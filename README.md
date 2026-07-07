# SCC BrainAI Learning

**Couche officielle d'apprentissage de BrainAI.**

BrainAI Learning **ne remplace pas** BrainAI Memory. La mémoire (11) conserve
l'**expérience brute et auditée** du Kernel. Learning (12) la **transforme en
apprentissages exploitables** : signaux, patterns, leçons, recommandations,
hypothèses — en **lecture seule** de la mémoire.

> **Garde-fou central : aucun apprentissage n'est jamais appliqué automatiquement.**
> Aucune auto-modification de doctrine, workflow, agent, mémoire, graphe ou code.
> Tout apprentissage est une **proposition traçable, vérifiable et révocable**,
> soumise à **validation humaine**. Stdlib pur, **déterministe**, sans réseau.

## Non-duplication & lecture seule

- **BrainAI Memory (11)** : lue via son interface **publique** (`search`,
  `export_dict`, `audit`) — **jamais modifiée**.
- Le seul espace d'écriture de Learning est **son propre registre de propositions**
  (`data/learnings.jsonl`). Il n'a **aucun** moyen de modifier une autre couche.

## Installation

```bash
cd 12_BRAINAI_LEARNING
python -m pip install -e .        # expose la commande `scc-brain-learning`
```

Aucune dépendance externe.

## Utilisation (CLI)

```bash
scc-brain-learning analyze                 # analyse la mémoire -> propositions
scc-brain-learning report                  # rapport d'apprentissage
scc-brain-learning learnings --kind recommendation
scc-brain-learning get <id>
scc-brain-learning validate <id> --by frederique --reason "utile"   # validation HUMAINE
scc-brain-learning reject   <id> --by frederique
scc-brain-learning revoke   <id> --by frederique
scc-brain-learning audit                   # intégrité + traçabilité + sûreté
scc-brain-learning export --format md
scc-brain-learning self-check
```

## Utilisation (Python)

```python
from scc_brainai_learning import LearningEngine

engine = LearningEngine()
engine.analyze()                           # produit des propositions (statut "proposed")
recos = engine.search(kind="recommendation")
engine.validate(recos[0]["id"], approver="frederique", reason="pertinent")  # humain requis
```

## Ce qui est produit

Signaux (patterns récurrents, erreurs récurrentes, préférences stables, workflows &
agents fréquents, zones faibles) · Patterns (regroupements) · Leçons ·
Recommandations · Hypothèses — **tous** scorés (confiance / fréquence / impact) et
**tracés** vers les événements mémoire sources.

## Composants

`LearningEngine` · `LearningSignal` · `LearningPattern` · `LearningLesson` ·
`LearningRecommendation` · `LearningHypothesis` · `LearningReport` (report.py) ·
`LearningIndex` · `HumanValidationPolicy` · analyse / scoring / regroupement /
synthèse / export / audit.

Détails : [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) ·
[`docs/LEARNING_MODEL.md`](docs/LEARNING_MODEL.md) ·
[`docs/ANALYSIS_SCORING.md`](docs/ANALYSIS_SCORING.md) ·
[`docs/GOVERNANCE_SAFETY.md`](docs/GOVERNANCE_SAFETY.md).

## Tests

```bash
python -m pytest -q      # 28 tests (déterministes, isolés)
```
