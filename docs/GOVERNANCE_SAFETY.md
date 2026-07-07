# Gouvernance & sûreté de l'apprentissage

> **Principe cardinal : aucun apprentissage autonome dangereux.** BrainAI Learning
> *propose* ; il n'*agit* jamais. Aucune auto-modification de doctrine, workflow,
> agent, mémoire, graphe ou code.

## 1. Tout est proposition

Chaque apprentissage naît au statut **`proposed`**. L'analyse ne peut produire que
des propositions — jamais un état validé ou appliqué.

## 2. Validation humaine obligatoire

Seule une **action humaine explicite** change un statut, via `HumanValidationPolicy` :

| Action | Transition | Exigence |
|--------|-----------|----------|
| `validate` | proposed → validated | approbateur **requis** |
| `reject` | proposed → rejected | approbateur requis |
| `revoke` | validated → revoked | approbateur requis |

- Sans approbateur → refus (`ValidationError`).
- Transition illégale (ex. `reject` après `validate`) → refus.
- Chaque décision est **tracée** : action, approbateur, motif, horodatage.

**Révocable** : une recommandation validée peut toujours être révoquée. Aucune
décision n'est irréversible côté Learning.

## 3. Aucune capacité d'auto-modification

Le `LearningEngine` **n'importe aucune API d'écriture** d'une autre couche. Son
unique espace de persistance est son registre de propositions
(`data/learnings.jsonl`). Il est donc **structurellement incapable** de modifier :
la mémoire (11), le graphe, une doctrine, un workflow, un agent, le Kernel ou du
code. La sûreté n'est pas une politique déclarative : c'est une **frontière
d'architecture**.

## 4. Audit de sûreté

`audit()` vérifie, à chaque appel :

- **intégrité** : l'empreinte de chaque apprentissage correspond à son contenu ;
- **traçabilité** : chaque `evidence` pointe vers une entrée mémoire réelle ;
- **sûreté** :
  - tout apprentissage non `proposed` porte un **approbateur humain** (aucune
    auto-validation) ;
  - aucun apprentissage n'est marqué `applied: true`.

Sur un registre sain : `audit.ok = true` (integrity + traceability + safety).

## 5. Ce que Learning ne fait jamais

- Modifier la mémoire ou toute autre couche.
- Appliquer une recommandation ou une hypothèse.
- Auto-valider une proposition.
- Émettre un appel réseau ou solliciter un LLM.

## 6. Alignement doctrinal

- **Traçabilité complète** ([[SCC-DOC-0016]]) : chaque proposition remonte à ses
  preuves.
- **Gouvernance avant extension** ([[SCC-DOC-0015]]) : rien ne s'applique sans
  validation.
- **Décisions immuables / ADR** : une proposition validée deviendrait, si adoptée,
  une décision formelle via le processus ADR — hors du périmètre automatique de
  Learning.
