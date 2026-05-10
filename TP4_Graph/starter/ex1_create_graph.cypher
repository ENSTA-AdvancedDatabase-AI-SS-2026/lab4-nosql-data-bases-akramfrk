// TP4 - Exercice 1 : Création du graphe UniConnect DZ
// Effacer la base pour partir propre
MATCH (n) DETACH DELETE n;

// ─── 1.1 : Contraintes d'unicité ─────────────────────────────────────────────
CREATE CONSTRAINT etudiant_id IF NOT EXISTS FOR (e:Etudiant) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT cours_code IF NOT EXISTS FOR (c:Cours) REQUIRE c.code IS UNIQUE;
CREATE CONSTRAINT competence_nom IF NOT EXISTS FOR (c:Competence) REQUIRE c.nom IS UNIQUE;

// ─── 1.2 : Créer les compétences ──────────────────────────────────────────────
UNWIND [
  {nom: "Python", categorie: "Programmation"},
  {nom: "Java", categorie: "Programmation"},
  {nom: "SQL", categorie: "Bases de Données"},
  {nom: "NoSQL", categorie: "Bases de Données"},
  {nom: "Machine Learning", categorie: "IA"},
  {nom: "Deep Learning", categorie: "IA"},
  {nom: "React", categorie: "Web"},
  {nom: "Docker", categorie: "DevOps"},
  {nom: "Linux", categorie: "Systèmes"},
  {nom: "Réseaux", categorie: "Infrastructure"}
] AS comp
MERGE (:Competence {nom: comp.nom, categorie: comp.categorie});

// ─── 1.3 : Créer les cours ────────────────────────────────────────────────────
UNWIND [
  {code: "INFO401", intitule: "Bases de Données Avancées", credits: 6, dept: "Informatique"},
  {code: "INFO402", intitule: "Intelligence Artificielle", credits: 6, dept: "Informatique"},
  {code: "INFO403", intitule: "Développement Web", credits: 4, dept: "Informatique"},
  {code: "INFO404", intitule: "Systèmes Distribués", credits: 5, dept: "Informatique"},
  {code: "INFO405", intitule: "Cloud Computing", credits: 4, dept: "Informatique"}
] AS cours
MERGE (:Cours {code: cours.code, intitule: cours.intitule, 
               credits: cours.credits, departement: cours.dept});

// ─── 1.4 : Créer les étudiants ────────────────────────────────────────────────
UNWIND range(1, 50) AS i
WITH i, 
     ["Ahmed", "Fatima", "Yanis", "Lina", "Karim", "Amina", "Mohamed", "Meriem", "Ali", "Sarah"][i % 10] AS prenom,
     ["Bensalem", "Ouali", "Mansouri", "Haddad", "Saidi", "Latreche", "Amrane", "Belkacem", "Djerar", "Messaoudi"][i % 10] AS nom,
     ["USTHB", "UMBB", "USTO", "UMC", "UBMA"][i % 5] AS universite,
     ["Informatique", "Mathématiques", "Electronique", "Telecoms", "GL"][i % 5] AS filiere,
     ["Alger", "Boumerdes", "Oran", "Constantine", "Annaba"][i % 5] AS ville
MERGE (e:Etudiant {id: "E" + i})
SET e.prenom = prenom, e.nom = nom, e.universite = universite, e.filiere = filiere, e.ville = ville, e.annee = (i % 5) + 1;

// Mettre au moins un "Yasmina" pour l'exercice 3.1
MATCH (e:Etudiant {id: "E50"}) SET e.prenom = "Yasmina";

// ─── 1.5 : Créer les relations ────────────────────────────────────────────────

// Relations CONNAIT (intra-université)
MATCH (e1:Etudiant), (e2:Etudiant)
WHERE e1.id <> e2.id AND rand() < 0.1 AND e1.universite = e2.universite
MERGE (e1)-[:CONNAIT {depuis: 2023, contexte: "Université"}]->(e2);

// Assurer connexité : chaque E a au moins un lien
MATCH (e1:Etudiant)
WITH e1
MATCH (e2:Etudiant) WHERE e1.id <> e2.id
WITH e1, e2 ORDER BY rand() LIMIT 1
MERGE (e1)-[:CONNAIT {depuis: 2024, contexte: "Evénement"}]-(e2);

// Relations SUIT (étudiant -> cours)
MATCH (e:Etudiant), (c:Cours)
WHERE rand() < 0.2
MERGE (e)-[:SUIT {semestre: "S" + e.annee, note: round(10 + rand() * 10)}]->(c);

// Relations MAITRISE (étudiant -> competence)
MATCH (e:Etudiant), (c:Competence)
WHERE rand() < 0.15
MERGE (e)-[:MAITRISE {niveau: ["Débutant", "Intermédiaire", "Avancé"][toInteger(rand()*3)]}]->(c);

// Cours -> Competence (REQUIERT)
MATCH (c:Cours), (comp:Competence)
WHERE rand() < 0.2
MERGE (c)-[:REQUIERT]->(comp);

// Vérification
MATCH (n) RETURN labels(n)[0] AS type, count(n) AS total ORDER BY total DESC;
MATCH ()-[r]->() RETURN type(r) AS relation, count(r) AS total ORDER BY total DESC;
