# Rapport TP4 - Neo4j (Graphes)

## 1. Schéma du graphe
Le modèle repose sur des noeuds fortement connectés représentant l'écosystème universitaire :
- `Etudiant` au centre, liés entre eux par `CONNAIT`.
- Liens sortants des étudiants : `SUIT` vers `Cours`, `MAITRISE` vers `Competence`, `MEMBRE_DE` vers `Club`, `A_STAGE_CHEZ` vers `Entreprise`.
- Liens internes entre entités : `Cours` - `REQUIERT` -> `Competence`.
Ce maillage dense permet des parcours complexes en temps réel sans souffrir du phénomène d'explosion combinatoire des JOIN SQL.

## 2. Résultats de l'algorithme de communautés (Louvain)
L'algorithme de Louvain, via la librairie GDS, assigne chaque nœud (Etudiant) à une "communityId" en maximisant la modularité (le nombre de connexions internes par rapport aux connexions externes).
Dans notre cas, les communautés générées correspondent très fortement aux `universite`s. En effet, lors de la génération du jeu de données, la probabilité pour deux étudiants de la même université de se connaître (`CONNAIT`) est bien plus grande que pour deux étudiants d'universités différentes. L'algorithme a donc naturellement détecté les "bulles sociales" que forment les campus universitaires (USTHB, UMBB, etc.).

## 3. Comparaison : SQL vs Cypher (Complexité & Lisibilité)
Prenons l'exemple de la requête : *"Amis d'amis d'Ahmed qui ne sont pas amis avec Ahmed"*
**En SQL :**
```sql
SELECT DISTINCT ami2.prenom 
FROM Etudiant e 
JOIN Connait c1 ON e.id = c1.id_etudiant1
JOIN Etudiant ami1 ON c1.id_etudiant2 = ami1.id
JOIN Connait c2 ON ami1.id = c2.id_etudiant1
JOIN Etudiant ami2 ON c2.id_etudiant2 = ami2.id
WHERE e.prenom = 'Ahmed' 
  AND ami2.id != e.id
  AND ami2.id NOT IN (
      SELECT id_etudiant2 FROM Connait WHERE id_etudiant1 = e.id
  );
```

**En Cypher :**
```cypher
MATCH (ahmed:Etudiant {prenom: "Ahmed"})-[:CONNAIT*2]-(suggestion)
WHERE NOT (ahmed)-[:CONNAIT]-(suggestion) AND ahmed <> suggestion
RETURN DISTINCT suggestion.prenom
```

**Conclusion :**
- **Lisibilité :** Cypher est "ASCII Art", on dessine visuellement le chemin `(a)-[:REL]-(b)`. C'est immensément plus intuitif que d'enchaîner mentalement des clés primaires/étrangères.
- **Complexité (Performance) :** SQL utilise de l'algèbre relationnelle sur des ensembles (Index Scans puis Hash/Merge Joins). Quand on cherche à x sauts, les tables intermédiaires explosent (complexité temporelle $O(n^k)$ avec $k$ sauts). Neo4j utilise "l'Index-Free Adjacency" : chaque noeud garde en mémoire des pointeurs directs vers ses voisins. Le coût de parcours dépend de la densité du chemin, pas de la taille totale du graphe. La requête en Cypher reste O(1) par rapport à la taille globale de la base de données.
