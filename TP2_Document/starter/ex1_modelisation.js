/**
 * TP2 - Exercice 1 : Modélisation MongoDB
 * Use Case : HealthCare DZ - Dossiers Médicaux
 */

use("medical_db");

// ─── 1.1 : Créer la collection avec validation ────────────────────────────────
db.createCollection("patients", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["cin", "nom", "prenom", "dateNaissance", "sexe"],
      properties: {
        cin: { bsonType: "string", description: "CIN obligatoire" },
        nom: { bsonType: "string", description: "Nom obligatoire" },
        prenom: { bsonType: "string", description: "Prenom obligatoire" },
        dateNaissance: { bsonType: "date", description: "Date de naissance obligatoire" },
        sexe: { enum: ["M", "F"], description: "Sexe doit être M ou F" },
        adresse: {
          bsonType: "object",
          required: ["wilaya", "commune"],
          properties: {
            wilaya: { bsonType: "string" },
            commune: { bsonType: "string" }
          }
        },
        groupeSanguin: { enum: ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"] },
        antecedents: { bsonType: "array", items: { bsonType: "string" } },
        allergies: { bsonType: "array", items: { bsonType: "string" } },
        consultations: {
          bsonType: "array",
          items: {
            bsonType: "object",
            required: ["id", "date", "medecin", "diagnostic"],
            properties: {
              id: { bsonType: "string" },
              date: { bsonType: "date" },
              medecin: {
                bsonType: "object",
                required: ["nom", "specialite"],
                properties: {
                  nom: { bsonType: "string" },
                  specialite: { bsonType: "string" }
                }
              },
              diagnostic: { bsonType: "string" }
            }
          }
        }
      }
    }
  }
});

// ─── 1.2 : Insérer des patients avec données algériennes ──────────────────────
const patients = [];
for (let i = 1; i <= 20; i++) {
  patients.push({
    cin: "1980010123" + i.toString().padStart(2, '0'),
    nom: "Patient" + i,
    prenom: "Prenom" + i,
    dateNaissance: new Date(1980 + (i % 20), (i % 12), (i % 28) + 1),
    sexe: i % 2 === 0 ? "M" : "F",
    adresse: { wilaya: i % 2 === 0 ? "Alger" : "Oran", commune: "Commune" + i },
    groupeSanguin: "O+",
    antecedents: i % 3 === 0 ? ["Diabète type 2", "HTA"] : [],
    allergies: i % 4 === 0 ? ["Pénicilline"] : [],
    consultations: [
      {
        id: "cons-" + i + "-1",
        date: new Date("2024-01-15"),
        medecin: { nom: "Dr. Mansouri", specialite: "Cardiologie" },
        diagnostic: i % 3 === 0 ? "Hypertension artérielle" : "Grippe",
        tension: { systolique: 120 + i, diastolique: 80 + i },
        medicaments: [{ nom: "Paracetamol", dosage: "1g", duree: "5 jours" }],
        notes: "RAS"
      },
      {
        id: "cons-" + i + "-2",
        date: new Date("2024-03-20"),
        medecin: { nom: "Dr. Latreche", specialite: "Généraliste" },
        diagnostic: "Contrôle de routine",
        tension: { systolique: 120, diastolique: 80 },
        medicaments: [],
        notes: "Bonne santé"
      }
    ]
  });
}

db.patients.insertMany(patients);

// ─── 1.3 : Collection analyses (référencée) ───────────────────────────────────
const patientsFromDb = db.patients.find().toArray();
const analyses = [];

patientsFromDb.forEach(p => {
  analyses.push({
    patient_id: p._id,
    date: new Date("2024-02-01"),
    type: "Glycémie",
    resultats: { valeur: 1.1 + (Math.random() * 0.5) },
    laboratoire: "Labo Central Alger",
    valide: true
  });
});

db.analyses.insertMany(analyses);

print("✅ Modélisation terminée. Patients insérés:", db.patients.countDocuments());
print("✅ Analyses insérées:", db.analyses.countDocuments());
