# Architecture de BrainAI Learning

## 1. Position dans SCC

BrainAI Learning (`12`) est la couche d'**apprentissage** au-dessus de BrainAI
Memory (`11`). Elle lit l'expérience et en dérive des **propositions** ; elle ne
pilote rien et ne modifie aucune autre couche.

```
   Kernel BrainAI (10) ── vit des cycles
        │  (expérience mémorisée)
   BrainAI Memory (11) ── search()/export_dict()/audit()  [interface publique, lecture seule]
        │
   ▶ BrainAI Learning (12) ── LearningEngine : analyse -> signaux -> patterns
        │                       -> leçons / recommandations / hypothèses (PROPOSITIONS)
   data/learnings.jsonl (registre de propositions — seul espace d'écriture)
```

## 2. Chaîne d'analyse (déterministe)

```
mémoire (entrées)
   │  MemorySource.entries()      # interface publique de la mémoire
   ▼
analysis.detect_signals()         # 1..7 : patterns, erreurs, préférences, workflows, agents, zones faibles
   ▼
grouping.group_signals()          # regroupement par catégorie -> patterns
   ▼
synthesis.synthesize()            # -> leçons, recommandations, hypothèses
   ▼
LearningEngine._merge()           # préserve les décisions humaines, met à jour les scores
   ▼
registre de propositions (statut "proposed")
```

Chaque étape est **pure** : mêmes entrées ⇒ mêmes apprentissages. Les identifiants
sont **dérivés du contenu** (idempotence : ré-analyser ne crée pas de doublon).

## 3. Composants

```
core/       config (as_of figé) · errors · clock (canonical/digest) · model (5 genres + statuts)
sources/    memory_source (mémoire BrainAI, lecture seule)
analysis    détecteurs -> signaux
scoring     confiance / fréquence / impact
grouping    signaux -> patterns
synthesis   patterns -> leçons / recommandations / hypothèses
validation  HumanValidationPolicy (garde-fou)
index       LearningIndex (recherche)
audit       intégrité + traçabilité + sûreté
report      LearningReport (JSON + Markdown)
engine      LearningEngine (façade)
cli         scc-brain-learning
```

## 4. Frontière de sûreté

Le `LearningEngine` **n'importe et n'appelle** aucune API d'écriture d'une autre
couche. Son unique persistance est son registre de propositions. Il ne peut donc,
par construction, ni modifier la mémoire, ni le graphe, ni une doctrine, ni un
agent, ni du code. Voir [`GOVERNANCE_SAFETY.md`](GOVERNANCE_SAFETY.md).

## 5. Invariants tenus

| Invariant | Comment |
|-----------|---------|
| Aucun moteur/Runtime/API/Control Plane/Kernel/Mémoire modifié | lecture seule via interface publique |
| Aucune auto-modification (doctrine, workflow, agent, mémoire, graphe, code) | aucun accès en écriture à ces couches |
| Tout apprentissage = proposition traçable/vérifiable/révocable | statut `proposed` + evidence + empreinte + cycle de validation |
| Validation humaine obligatoire | `HumanValidationPolicy` (approbateur requis) |
| Aucun LLM / réseau / dépendance externe | stdlib pur |
| Déterminisme maximal | identifiants de contenu + horodatage figé + règles pures |
