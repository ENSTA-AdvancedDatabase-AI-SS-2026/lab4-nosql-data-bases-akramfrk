# Rapport TP5 - Performance & Optimisation NoSQL

## Tableau de Recommandation

| Critère | Redis | MongoDB | Cassandra | Neo4j |
|---------|-------|---------|-----------|-------|
| **Débit écriture** | ★★★★★ (In-memory, O(1), pipelines ultra-rapides) | ★★★☆☆ (Disk/B-Tree, IO lock par document, BulkOps requis) | ★★★★★ (Log-structured merge tree, optimisé append-only, leaderless) | ★★☆☆☆ (Index updates lourds, verrouillage ACID global) |
| **Débit lecture** | ★★★★★ (Mémoire RAM, très faible latence) | ★★★★☆ (Bonne latence si la donnée est dans le working set en RAM) | ★★★★☆ (O(1) si clé de partition fournie, très lent sinon) | ★★★☆☆ (Parcours de graphe coûteux mais plus rapide que SQL JOINs) |
| **Requêtes complexes** | ★☆☆☆☆ (Support quasi nul, quelques scripts LUA ou modules limités) | ★★★★☆ (Aggregation Pipeline très puissant, Indexation riche) | ★☆☆☆☆ (Pas de JOIN, pas d'agrégation, nécessite Spark) | ★★★★★ (Cypher et GDS, conçu nativement pour les requêtes complexes) |
| **Scalabilité** | ★★★☆☆ (Sharding (Redis Cluster) possible mais limité par la taille de la RAM) | ★★★★☆ (Sharding natif géré au niveau du cluster) | ★★★★★ (Architecture Masterless, scalabilité horizontale linéaire infinie) | ★★☆☆☆ (Assez difficile à scaler horizontalement pour l'écriture) |
| **Use case idéal** | **Cache**, Leaderboard, Sessions, Pub/Sub, File d'attente temps réel | **Documents**, CMS, Catalogues de produits, Profils Utilisateurs flexibles | **IoT/Logs**, Time Series, Massive write volume, High Availability | **Graphe**, Réseaux sociaux, Moteurs de recommandation, Lutte contre la Fraude |

## Synthèse et Recommandation Architecturale

Le choix de la base de données ne dépend pas de laquelle est "la plus rapide" en absolu, mais de **l'adéquation avec le pattern d'accès (Workload)** de l'application.

1. **Redis** : À privilégier comme couche transactionnelle temps réel et en **Cache-Aside**. Idéal pour absorber des pics d'accès sur des données volatiles et isolées.
2. **Cassandra** : À privilégier pour les données de télémétrie, compteurs industriels ou journaux d'événements. Il absorbe les écritures massives sans ciller. La modélisation **doit être dictée par la requête**.
3. **MongoDB** : Le couteau suisse. À privilégier pour les données "métier" hétérogènes (fiches clients, catalogues). Il offre le meilleur compromis entre souplesse de modélisation (JSON) et requêtabilité (Aggregations, Index).
4. **Neo4j** : À utiliser conjointement avec l'une des autres bases, uniquement pour modéliser le tissu relationnel complexe (ex: détection de fraude impliquant 5 sauts entre entités).

> **Conclusion pour le système :** Une architecture moderne "Polyglot Persistence" utiliserait **MongoDB** comme base principale, **Redis** en façade pour le cache, **Cassandra** en asynchrone pour les logs, et éventuellement **Neo4j** pour les fonctionnalités sociales.
