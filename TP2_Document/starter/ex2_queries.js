/**
 * TP2 - Exercice 2 : Requêtes de Base
 */

use("medical_db");

// 2.1 Trouver tous les patients diabétiques de plus de 50 ans à Alger
const d = new Date();
d.setFullYear(d.getFullYear() - 50);
db.patients.find({
  "adresse.wilaya": "Alger",
  antecedents: "Diabète type 2",
  dateNaissance: { $lt: d }
});

// 2.2 Patients allergiques à la Pénicilline avec au moins 3 consultations
db.patients.find({
  allergies: "Pénicilline",
  "consultations.2": { $exists: true }
});

// 2.3 Projection : Nom, prénom, et dernière consultation seulement
db.patients.find({}, {
  nom: 1,
  prenom: 1,
  consultations: { $slice: -1 }
});

// 2.4 Patients sans antécédents dont la tension systolique > 140 en dernière consultation
db.patients.aggregate([
  { $match: { antecedents: { $size: 0 } } },
  { $addFields: { lastConsult: { $arrayElemAt: ["$consultations", -1] } } },
  { $match: { "lastConsult.tension.systolique": { $gt: 140 } } }
]);

// 2.5 Recherche textuelle sur les diagnostics (créer index text d'abord)
db.patients.createIndex({ "consultations.diagnostic": "text" });
db.patients.find({
  $text: { $search: "Hypertension" }
});
