-- 3.1 Mesures d'un capteur spécifique sur les dernières 6 heures
SELECT * FROM mesures_par_capteur
WHERE capteur_id = 123e4567-e89b-12d3-a456-426614174000 
  AND date_jour = '2024-05-10' 
  AND timestamp >= '2024-05-10 10:00:00';

-- 3.2 Dernière mesure de chaque capteur d'une wilaya
-- Cassandra ne permet pas de faire facilement un "GROUP BY wilaya" avec un fetch de la dernière mesure si la partition key n'est pas optimisée pour.
-- Si nous avions une table "dernieres_mesures_par_wilaya (wilaya, capteur_id, timestamp...) PRIMARY KEY (wilaya, capteur_id)", 
-- On pourrait interroger cette table. Avec la table actuelle, ce n'est pas performant sans ALLOW FILTERING ou faire N requêtes côté application.

-- 3.3 Capteurs en alerte dans la wilaya "Alger" aujourd'hui
SELECT * FROM alertes_par_wilaya
WHERE wilaya = 'Alger' AND date_jour = '2024-05-10';

-- 3.4 Consommation totale par heure sur une journée (dashboard)
SELECT date_heure, puissance_moy_kw FROM agregats_horaires
WHERE wilaya = 'Alger' 
  AND date_heure >= '2024-05-10 00:00:00' 
  AND date_heure <= '2024-05-10 23:59:59';

-- 3.5 Détection d'anomalie : capteurs avec tension < 200V ou > 240V
-- Dans Cassandra, faire une requête sur des données non-indexées par la clé de partition est inefficace.
-- Il faut créer une table "anomalies_tension (date_jour, timestamp, capteur_id, tension_v) PRIMARY KEY (date_jour, timestamp)" ou analyser via Spark.

-- 3.6 Top 10 capteurs les plus actifs (plus de mesures) cette semaine
-- Cassandra n'est pas fait pour les agrégations complexes comme un "Top 10" avec un GROUP BY global (tous les capteurs). 
-- Il est nécessaire d'utiliser Apache Spark (Spark Cassandra Connector) pour calculer cela, ou maintenir une table "compteurs_capteurs" incrementée côté application.

-- 3.7 Requête ALLOW FILTERING : Pourquoi éviter ?
-- ALLOW FILTERING force Cassandra à parcourir potentiellement toutes les partitions de la base pour trouver les données.
-- C'est un anti-pattern majeur en production car cela ne scale pas (les performances s'effondrent quand les données augmentent).
-- Pour corriger ça, il faut toujours modéliser une table dont la PRIMARY KEY permet de satisfaire la requête sans ALLOW FILTERING.
