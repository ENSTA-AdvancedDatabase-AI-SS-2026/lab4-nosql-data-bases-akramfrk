/**
 * TP2 - Exercice 4 : Index et Optimisation
 */

use("medical_db");

// ─── 4.1 : Créer les index appropriés ────────────────────────────────────────

// Index 1 : Recherche fréquente par wilaya + antécédents
db.patients.createIndex({ "adresse.wilaya": 1, antecedents: 1 });

// Index 2 : Recherche par date de consultation
db.patients.createIndex({ "consultations.date": -1 });

// Index 3 : Texte sur diagnostics pour recherche full-text
db.patients.createIndex({ "consultations.diagnostic": "text" });

// Index 4 : Analyses par patient (lookup)
db.analyses.createIndex({ patient_id: 1 });

// ─── 4.2 : Comparer avec explain() ────────────────────────────────────────────

// Requête de test
const requeteTest = {
  "adresse.wilaya": "Alger",
  antecedents: "Diabète type 2"
};

print("=== AVANT index ===");
db.patients.dropIndex({ "adresse.wilaya": 1, antecedents: 1 });
let statsAvant = db.patients.explain("executionStats").find(requeteTest);
print(`nReturned: ${statsAvant.executionStats.nReturned}`);
print(`totalDocsExamined: ${statsAvant.executionStats.totalDocsExamined}`);
print(`executionTimeMillis: ${statsAvant.executionStats.executionTimeMillis}`);

print("\n=== APRÈS index ===");
db.patients.createIndex({ "adresse.wilaya": 1, antecedents: 1 });
let statsApres = db.patients.explain("executionStats").find(requeteTest);
print(`nReturned: ${statsApres.executionStats.nReturned}`);
print(`totalDocsExamined: ${statsApres.executionStats.totalDocsExamined}`);
print(`executionTimeMillis: ${statsApres.executionStats.executionTimeMillis}`);

// ─── 4.4 : Index TTL pour archivage ───────────────────────────────────────────
db.analyses.createIndex(
  { date: 1 },
  { expireAfterSeconds: 5 * 365 * 24 * 60 * 60 } // 5 ans en secondes
);
