-- TP3 - Exercice 1 : Schéma Cassandra
-- Use Case : SmartGrid DZ - IoT Électrique

-- ─── 1.1 : Créer le Keyspace ──────────────────────────────────────────────────
CREATE KEYSPACE smartgrid
WITH replication = {'class': 'NetworkTopologyStrategy', 'datacenter1': 1}
AND durable_writes = true;

USE smartgrid;

-- ─── 1.2 : Table mesures_par_capteur ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS mesures_par_capteur (
  capteur_id   UUID,
  date_jour    DATE,
  timestamp    TIMESTAMP,
  wilaya       TEXT,
  commune      TEXT,
  tension_v    FLOAT,
  courant_a    FLOAT,
  puissance_kw FLOAT,
  frequence_hz FLOAT,
  temperature  FLOAT,
  alerte       BOOLEAN,
  code_alerte  TEXT,
  PRIMARY KEY ((capteur_id, date_jour), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC)
  AND default_time_to_live = 7776000;  -- 90 jours en secondes


-- ─── 1.3 : Table alertes_par_wilaya ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS alertes_par_wilaya (
  wilaya       TEXT,
  date_jour    DATE,
  timestamp    TIMESTAMP,
  capteur_id   UUID,
  code_alerte  TEXT,
  description  TEXT,
  gravite      INT,   -- 1=info, 2=warning, 3=critique
  resolue      BOOLEAN,
  PRIMARY KEY ((wilaya, date_jour), timestamp, capteur_id)
) WITH CLUSTERING ORDER BY (timestamp DESC)
  AND default_time_to_live = 31536000;  -- 1 an


-- ─── 1.4 : Table agregats_horaires ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS agregats_horaires (
  wilaya            TEXT,
  date_heure        TIMESTAMP,
  nb_capteurs       INT,
  puissance_moy_kw  FLOAT,
  puissance_max_kw  FLOAT,
  puissance_min_kw  FLOAT,
  nb_alertes        INT,
  PRIMARY KEY ((wilaya), date_heure)
) WITH CLUSTERING ORDER BY (date_heure DESC)
  AND default_time_to_live = 157680000;  -- 5 ans


-- Vérification
DESCRIBE TABLES;
