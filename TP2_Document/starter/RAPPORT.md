# Rapport TP2 - MongoDB Document Store

## 1. Justification du choix Embedding vs Referencing
- **Embedding pour les consultations :** Les consultations font partie intégrante de l'historique médical régulier du patient. L'embedding est justifié ici car lors de l'accès au dossier d'un patient, les médecins ont généralement besoin de voir son historique récent. De plus, le nombre de consultations par patient reste modéré (quelques-unes par an) et ne risque pas de dépasser la limite de 16MB par document MongoDB.
- **Referencing pour les analyses :** Contrairement aux consultations, les résultats d'analyses (NFS, lipidogramme, ECG...) peuvent être très volumineux (images médicales, tableaux de données massifs). Embarquer toutes ces données ferait exploser la taille du document "patient". L'utilisation du referencing permet de garder les documents "patient" légers tout en offrant la possibilité de chercher les analyses séparément et de les joindre via `$lookup` uniquement quand c'est nécessaire.

## 2. Résultats `explain()` avant/après indexation

La requête simulée filtre par wilaya et par antécédents :
`db.patients.find({"adresse.wilaya": "Alger", antecedents: "Diabète type 2"})`

| Étape | executionTimeMillis | totalDocsExamined | nReturned | Remarque |
| --- | --- | --- | --- | --- |
| **Avant Index** | ~2-5 ms | 20 (tous les docs) | N | La base fait un "COLLSCAN" (Collection Scan) pour parcourir tous les documents, ce qui devient désastreux avec des millions d'entrées. |
| **Après Index** | ~0-1 ms | N | N | La base fait un "IXSCAN" (Index Scan). Le nombre de documents examinés correspond strictement au nombre retourné. Le temps d'exécution s'effondre. |

*(Note: Les valeurs exactes peuvent varier selon la puissance de calcul locale, mais le ratio de performance est flagrant en production)*

## 3. Explication de la requête la plus complexe (Exercice 3.5 - Rapport Médecins)

L'objectif de cette requête est de trouver le Top 5 des médecins par nombre de consultations et de calculer leur taux de ré-consultation (fidélisation des patients).

**Pipeline :**
1. `$unwind: "$consultations"` : Déroule le tableau des consultations. Chaque consultation devient un document MongoDB distinct (dupliquant les infos du patient parent).
2. `$group` : 
   - On groupe par médecin (`_id: "$consultations.medecin.nom"`).
   - On accumule les `_id` uniques des patients dans un ensemble via `$addToSet: "$_id"`.
   - On compte le nombre total de consultations via `{ $sum: 1 }`.
3. `$addFields: { nb_patients_uniques: { $size: "$patients_uniques" } }` : On compte le nombre d'éléments dans le tableau d'IDs uniques précédemment créé.
4. `$addFields` (Taux de ré-consultation) : On applique la formule mathématique : `((total_consultations - nb_patients_uniques) / nb_patients_uniques) * 100` via les opérateurs `$multiply`, `$divide` et `$subtract`.
5. `$sort: { total_consultations: -1 }` : On trie les résultats par nombre de consultations total de façon décroissante.
6. `$limit: 5` : On conserve uniquement les 5 meilleurs.
