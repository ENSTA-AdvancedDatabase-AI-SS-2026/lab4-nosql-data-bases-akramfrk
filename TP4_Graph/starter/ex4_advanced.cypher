// TP4 - Exercice 4 : Requêtes Avancées

// 4.1 Trouver un tuteur
// "Étudiant en Master qui maîtrise Python et a eu >14/20 en BDD"
MATCH (tuteur:Etudiant)-[:MAITRISE]->(comp:Competence {nom: "Python"})
MATCH (tuteur)-[s:SUIT]->(cours:Cours {intitule: "Bases de Données Avancées"})
WHERE tuteur.annee >= 4 AND s.note > 14
RETURN tuteur.prenom, tuteur.nom, s.note AS note_BDD;

// 4.2 Réseau alumni dans une entreprise
// "Qui de mon réseau (jusqu'à 3 sauts) travaille chez Sonatrach ?"
// (On suppose qu'il y a un noeud Entreprise Sonatrach et relation A_STAGE_CHEZ)
MATCH (moi:Etudiant {prenom: "Ahmed"})-[:CONNAIT*1..3]-(alumni:Etudiant)-[:A_STAGE_CHEZ]->(e:Entreprise {nom: "Sonatrach"})
RETURN DISTINCT alumni.prenom, alumni.nom;

// 4.3 Détection de ponts
// Quels étudiants connectent des communautés isolées ?
// On utilise la centralité d'intermédiarité (Betweenness Centrality)
CALL gds.betweenness.stream('reseau_social')
YIELD nodeId, score
RETURN gds.util.asNode(nodeId).prenom AS etudiant, score AS importance_pont
ORDER BY score DESC
LIMIT 5;

// 4.4 Analyse temporelle
// Croissance du réseau : nouvelles connexions par mois (ici par année dans nos datas)
MATCH ()-[r:CONNAIT]->()
RETURN r.depuis AS annee_connexion, count(r)/2 AS nouvelles_connexions
ORDER BY annee_connexion;

// 4.5 Score de similarité
// Étudiants les plus similaires à Ahmed (cours, compétences, clubs)
// Utiliser le coefficient de Jaccard
MATCH (ahmed:Etudiant {prenom: "Ahmed"})-[:SUIT|MAITRISE|MEMBRE_DE]->(n)
WITH ahmed, collect(id(n)) AS ahmed_nodes
MATCH (autre:Etudiant)-[:SUIT|MAITRISE|MEMBRE_DE]->(m)
WHERE autre <> ahmed
WITH ahmed, autre, ahmed_nodes, collect(id(m)) AS autre_nodes
WITH ahmed, autre, ahmed_nodes, autre_nodes,
     gds.similarity.jaccard(ahmed_nodes, autre_nodes) AS similarite
WHERE similarite > 0
RETURN autre.prenom, autre.nom, similarite
ORDER BY similarite DESC
LIMIT 5;
