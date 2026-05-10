# Rapport TP3 - Cassandra (Séries Temporelles)

## 1. Justification de chaque Partition Key (risque de hot partition ?)
- `mesures_par_capteur` : La Partition Key est composée de `(capteur_id, date_jour)`. L'utilisation combinée du capteur et du jour précis (bucketing) permet d'éviter qu'un capteur émettant pendant 10 ans ne crée une partition géante (une "hot partition"). Chaque capteur aura une partition distincte par jour, garantissant une bonne distribution sur le cluster.
- `alertes_par_wilaya` : La Partition Key est `(wilaya, date_jour)`. Si l'on utilisait uniquement `wilaya`, les grandes villes comme Alger auraient des partitions massives comparées aux autres wilayas, et ce volume ne ferait que croître indéfiniment. L'ajout de la date permet de découper cette partition en portions journalières maîtrisées.
- `agregats_horaires` : La Partition Key est `(wilaya)`. Étant donné qu'il ne s'agit que d'agrégats (1 ligne par heure = 24 lignes/jour = 8760 lignes/an), le volume de données par wilaya reste très modeste sur de nombreuses années. Il n'y a donc pas de risque critique de hot partition ici, même sans bucketing par date.

## 2. Pourquoi ALLOW FILTERING est dangereux en production
Dans Cassandra, les requêtes performantes accèdent aux données via la Partition Key (pour identifier le noeud) et la Clustering Key (pour la recherche séquentielle sur disque).
L'instruction `ALLOW FILTERING` permet d'exécuter une requête ne respectant pas ces clés. Cassandra sera alors obligé de parcourir, au pire, la totalité des données du cluster (Full Table Scan distribué) pour appliquer le filtre.
En production, avec des milliards d'enregistrements, cette requête monopolise le réseau, la RAM et le CPU de l'ensemble du cluster, provoquant des timeouts, un ralentissement général et possiblement l'effondrement des noeuds.

## 3. Comparaison TWCS vs STCS vs LCS : quand utiliser chacun ?
- **TWCS (TimeWindowCompactionStrategy)** : 
  - **Cas d'usage :** Idéal pour les données de séries temporelles pures avec TTL (ex: IoT, logs). 
  - **Raison :** Il groupe les SSTables par fenêtre de temps. Quand toutes les données d'une fenêtre ont expiré via leur TTL, le SSTable entier est supprimé (Drop) au lieu de compacter ligne par ligne, offrant un énorme gain en I/O.
- **STCS (SizeTieredCompactionStrategy)** :
  - **Cas d'usage :** Idéal pour les tables avec beaucoup d'insertions (Write-heavy) et peu de mises à jour/suppressions. (C'est la stratégie par défaut).
  - **Raison :** Moins gourmande en ressources, elle fusionne des SSTables de tailles similaires, optimisant les écritures au détriment de l'espace disque lors de la compaction.
- **LCS (LeveledCompactionStrategy)** :
  - **Cas d'usage :** Idéal pour des données très lues (Read-heavy) avec beaucoup de mises à jour (Updates/Deletes).
  - **Raison :** Compaction très agressive en arrière-plan pour garantir que les données sont lues sur très peu de fichiers SSTables (souvent un seul niveau). Cela coûte cher en écritures (Write Amplification) mais garantit des requêtes de lecture extrêmement prédictibles.
