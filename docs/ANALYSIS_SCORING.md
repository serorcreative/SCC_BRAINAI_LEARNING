# Analyse & scoring

## 1. Détecteurs (mémoire → signaux)

Tous déterministes, purs, tracés vers les événements sources.

| # | Détection | Source (sous-type mémoire) | Catégorie |
|---|-----------|----------------------------|-----------|
| 2 | Patterns récurrents (intentions) | `intent` | `intent_recurrence` |
| 5 | Workflows fréquents (signatures d'actions) | `plan` | `workflow_frequency` |
| 6 | Agents fréquemment mobilisés | `agents` | `agent_mobilization` |
| 3 | Erreurs récurrentes | `error` | `error_recurrence` |
| 4 | Préférences stables / conflits | `preference` | `preference_stability` / `preference_conflict` |
| 7 | Zones faibles (taux d'erreur, faible diversité) | `error`, `intent` | `weak_zone` |

Un signal n'est retenu qu'au-delà du seuil `min_frequency` (défaut 2). Les seuils
sont configurables (`thresholds` dans `config/learning.json`).

## 2. Scoring

Chaque apprentissage porte trois mesures bornées :

- **fréquence** : nombre d'occurrences observées (entier).
- **confiance** ∈ [0,1] : moyenne de
  - la **fréquence normalisée** `min(1, frequency / strong_frequency)` et
  - la **consistance** `count / total` (proportion sur les cycles observés).
- **impact** ∈ [0,1] : pondération par catégorie —
  `error_recurrence` 0.9 · `weak_zone` 0.8 · `preference_conflict` 0.6 ·
  `intent_recurrence` / `workflow_frequency` 0.5 · `agent_mobilization` 0.4 ·
  `preference_stability` 0.2.

Les recommandations sont classées par **impact × confiance** (déterministe).

## 3. Regroupement (signaux → patterns)

Les signaux d'une même catégorie sont regroupés en un `LearningPattern` :
- `evidence` = union des preuves des signaux ;
- `frequency` = somme ; `confidence` = max ; `impact` = pondération de catégorie ;
- `data.signals` = ids des signaux regroupés (traçabilité).

## 4. Synthèse (patterns → leçons / recommandations / hypothèses)

Règles déterministes par catégorie :

| Catégorie | Leçon | Recommandation | Hypothèse |
|-----------|-------|----------------|-----------|
| intent_recurrence | ✅ | — | — |
| workflow_frequency | ✅ | ✅ | ✅ |
| agent_mobilization | ✅ | ✅ (bonne pratique) | — |
| error_recurrence | ✅ | ✅ | ✅ |
| weak_zone | ✅ | ✅ | ✅ |
| preference_stability | ✅ | ✅ | — |
| preference_conflict | ✅ | ✅ | ✅ |

Chaque dérivation **cite** son pattern (`from_pattern`) et hérite de ses preuves —
la chaîne aval → amont reste intacte.

## 5. Déterminisme

Itérations triées, identifiants dérivés du contenu, horodatage figé (`as_of`),
formules pures : deux analyses de la même mémoire produisent des apprentissages
**strictement identiques** (vérifié en processus et **cross-process**).
