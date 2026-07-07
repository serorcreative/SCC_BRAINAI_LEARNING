# Modèle d'apprentissage

## 1. Les cinq genres

Tous héritent d'un tronc commun (`LearningItem`) et sont **propositionnels**.

| Genre | `kind` | Sens |
|-------|--------|------|
| **LearningSignal** | `signal` | observation atomique / signal faible détecté |
| **LearningPattern** | `pattern` | régularité récurrente (regroupement de signaux) |
| **LearningLesson** | `lesson` | leçon apprise, lisible |
| **LearningRecommendation** | `recommendation` | recommandation actionnable **proposée** |
| **LearningHypothesis** | `hypothesis` | hypothèse d'amélioration à tester |

## 2. Structure d'un apprentissage

```json
{
  "id": "recommendation_ab12cd34ef56",
  "kind": "recommendation",
  "title": "Recommandation : error recurrence",
  "detail": "Proposer d'ajouter une vérification préalable ciblant l'erreur récurrente (proposition, non appliquée).",
  "evidence": ["mem_000000000007", "mem_00000000000e"],
  "confidence": 0.7, "frequency": 3, "impact": 0.9,
  "status": "proposed",
  "created_at": "2026-07-06T00:00:00+00:00",
  "tags": ["recommendation", "error_recurrence", "proposal"],
  "data": { "category": "error_recurrence", "from_pattern": "pattern_…", "applied": false },
  "validation": {},
  "hash": "sha256(contenu + scores)"
}
```

- **id** : dérivé du contenu (déterministe, idempotent) → même détection, même id.
- **evidence** : identifiants d'**entrées mémoire sources** (traçabilité complète).
- **hash** : empreinte du contenu + scores (vérifiable ; l'audit détecte toute
  altération).
- **status** / **validation** : cycle de validation humaine (voir
  [`GOVERNANCE_SAFETY.md`](GOVERNANCE_SAFETY.md)).

## 3. Cycle de statut

```
proposed ──▶ validated ──▶ revoked
   └──▶ rejected
```

Seule une **action humaine** (approbateur requis) fait transiter un apprentissage.
L'analyse ne produit que du `proposed`.

## 4. Traçabilité (aval → amont)

```
Recommendation ──from_pattern──▶ Pattern ──signals──▶ Signal ──evidence──▶ entrées mémoire (11)
```

Toute proposition remonte jusqu'aux **événements mémoire** qui la justifient ;
l'audit vérifie que chaque `evidence` existe réellement dans la mémoire.

## 5. Idempotence & mise à jour

Ré-analyser la même mémoire produit **exactement** les mêmes apprentissages (mêmes
ids). Si la mémoire grandit, les scores se mettent à jour mais les **décisions
humaines** (validated/rejected/revoked) sont **préservées**.
