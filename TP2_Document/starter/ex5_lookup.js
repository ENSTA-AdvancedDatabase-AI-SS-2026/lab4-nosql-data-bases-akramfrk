/**
 * TP2 - Exercice 5 : $lookup
 */

use("medical_db");

// 5.1 Joindre patients et analyses pour récupérer le dossier complet d'un patient
db.patients.aggregate([
  {
    $lookup: {
      from: "analyses",
      localField: "_id",
      foreignField: "patient_id",
      as: "dossier_analyses"
    }
  }
]);

// 5.2 Trouver les patients dont la glycémie dépasse 1.26 g/L
db.analyses.aggregate([
  { $match: { type: "Glycémie", "resultats.valeur": { $gt: 1.26 } } },
  {
    $lookup: {
      from: "patients",
      localField: "patient_id",
      foreignField: "_id",
      as: "patient_info"
    }
  },
  { $unwind: "$patient_info" }
]);

// 5.3 Statistiques croisées : taux d'analyses anormales par wilaya
db.analyses.aggregate([
  {
    $lookup: {
      from: "patients",
      localField: "patient_id",
      foreignField: "_id",
      as: "patient_info"
    }
  },
  { $unwind: "$patient_info" },
  {
    $group: {
      _id: "$patient_info.adresse.wilaya",
      totalAnalyses: { $sum: 1 },
      analysesAnormales: {
        $sum: {
          $cond: [
            { $or: [
              { $and: [{ $eq: ["$type", "Glycémie"] }, { $gt: ["$resultats.valeur", 1.26] }] }
            ]},
            1,
            0
          ]
        }
      }
    }
  },
  {
    $project: {
      tauxAnormales: {
        $multiply: [ { $divide: ["$analysesAnormales", "$totalAnalyses"] }, 100 ]
      }
    }
  }
]);
