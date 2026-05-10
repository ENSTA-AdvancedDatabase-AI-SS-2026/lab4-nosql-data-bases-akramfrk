-- 4.1 Choisir la stratégie de compaction pour chaque table
-- Pour les séries temporelles IoT, TimeWindowCompactionStrategy (TWCS) est la stratégie de compaction idéale.
-- Les données arrivent triées chronologiquement. TWCS va grouper les données par fenêtre de temps (ex: 1 jour).
-- Quand toutes les données d'une fenêtre arrivent à expiration (TTL), le fichier SSTable entier est supprimé sans coût d'I/O (pas de compaction nécessaire pour purger).

-- 4.2 Configurer TWCS pour les mesures
ALTER TABLE smartgrid.mesures_par_capteur
WITH compaction = {
  'class': 'TimeWindowCompactionStrategy',
  'compaction_window_unit': 'DAYS',
  'compaction_window_size': 1
};

-- 4.3 Vérifier l'utilisation des TTL
-- Impossible de requêter directement le TTL via SELECT sans utiliser la fonction TTL().
SELECT capteur_id, TTL(tension_v) FROM smartgrid.mesures_par_capteur LIMIT 10;

-- 4.4 Analyser une partition "hot" : comment la détecter et la corriger ?
-- Détection: `nodetool cfhistograms smartgrid mesures_par_capteur` permet d'analyser la distribution des tailles de partitions et repérer des "outliers".
-- Correction: Il faut changer la clé de partition (ajouter du "bucketing"). Par exemple, si la clé est juste (wilaya), 
-- la partition d'Alger sera énorme. On utilise plutôt (wilaya, date_jour) pour limiter la taille de chaque partition à une journée.
