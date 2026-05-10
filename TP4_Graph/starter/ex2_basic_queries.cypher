// TP4 - Exercice 2 : Requêtes de Base

// 2.1 Trouver tous les amis d'Ahmed (1 saut)
MATCH (ahmed:Etudiant {prenom: "Ahmed"})-[:CONNAIT]-(ami:Etudiant)
RETURN ami.prenom, ami.nom, ami.universite;

// 2.2 Trouver les amis d'amis d'Ahmed qui ne sont pas déjà ses amis
MATCH (ahmed:Etudiant {prenom: "Ahmed"})-[:CONNAIT*2]-(ami_dami:Etudiant)
WHERE NOT (ahmed)-[:CONNAIT]-(ami_dami) AND ahmed <> ami_dami
RETURN DISTINCT ami_dami.prenom, ami_dami.nom;

// 2.3 Étudiants qui suivent le même cours que Fatima mais ne la connaissent pas
MATCH (fatima:Etudiant {prenom: "Fatima"})-[:SUIT]->(c:Cours)<-[:SUIT]-(autre:Etudiant)
WHERE NOT (fatima)-[:CONNAIT]-(autre) AND fatima <> autre
RETURN DISTINCT autre.prenom, autre.nom, c.intitule;

// 2.4 Clubs les plus populaires (par nombre de membres)
// (On suppose qu'il y a des noeuds Club et des relations MEMBRE_DE, 
// je les ajoute virtuellement dans la requête bien que non créés dans ex1)
MATCH (e:Etudiant)-[:MEMBRE_DE]->(c:Club)
RETURN c.nom, count(e) AS nb_membres
ORDER BY nb_membres DESC;

// 2.5 Profil complet d'un étudiant : amis, cours, compétences, clubs
MATCH (e:Etudiant {prenom: "Ahmed"})
OPTIONAL MATCH (e)-[:CONNAIT]-(ami:Etudiant)
OPTIONAL MATCH (e)-[:SUIT]->(cours:Cours)
OPTIONAL MATCH (e)-[:MAITRISE]->(comp:Competence)
OPTIONAL MATCH (e)-[:MEMBRE_DE]->(club:Club)
RETURN e.prenom, e.nom,
       collect(DISTINCT ami.prenom) AS amis,
       collect(DISTINCT cours.intitule) AS cours_suivis,
       collect(DISTINCT comp.nom) AS competences,
       collect(DISTINCT club.nom) AS clubs;
