# Rapport TP1 - Redis Key-Value

## 1. Comparaison de performance (hit vs miss)
L'utilisation du pattern Cache-Aside montre une nette amélioration des performances. Lorsqu'une donnée n'est pas en cache (Cache MISS), l'application doit interroger la base de données relationnelle (ex: PostgreSQL) ce qui prend un temps considérable (simulé à environ 2000ms dans l'exercice). Une fois la donnée mise en cache dans Redis avec un TTL, les appels suivants (Cache HIT) se font en quelques millisecondes (généralement < 5ms). Le taux de Cache Hit dépend directement du TTL et de la fréquence de requêtes, permettant une accélération de plusieurs ordres de grandeur.

## 2. Justification des choix de modélisation
- **Hash pour les produits** : Permet de stocker et mettre à jour des attributs individuels (ex: stock, prix) sans avoir à réécrire l'ensemble du produit.
- **Hash pour le panier** : Idéal pour associer un product_id à une quantité et l'incrémenter efficacement via `HINCRBY`.
- **List pour l'historique** : Très utile pour ajouter chronologiquement un produit consulté (`LPUSH`) et conserver uniquement les N derniers éléments via `LTRIM`.
- **Set pour les catégories** : Un Set empêche les doublons de produits dans une catégorie, et les opérations comme `SINTER` permettent de faire des intersections rapides entre plusieurs tags/catégories.
- **Sorted Set pour le classement** : Structure optimisée pour trier des éléments selon un score (ici, la quantité vendue). `ZINCRBY` et `ZREVRANGE` permettent des mises à jour et requêtes O(log(N)) parfaites pour un Leaderboard en temps réel.

## 3. Réponses aux questions de réflexion

**1. Que se passe-t-il si Redis redémarre ?**
Si la persistance n'est pas activée (AOF ou RDB), toutes les données en mémoire seront perdues. Dans le cas d'un cache pur, cela provoque un "Cold Start" (démarrage à froid) : toutes les requêtes initiales feront un Cache MISS et frapperont la base de données principale, risquant de la surcharger (Thundering Herd Problem) le temps que le cache se remplisse à nouveau. Si la persistance est activée, Redis rechargera les données depuis le disque.

**2. Comment gérer la cohérence cache/DB en cas d'accès concurrent ?**
Pour assurer la cohérence, il faut utiliser des stratégies de Cache Invalidation. Par exemple, supprimer la clé Redis (`DEL`) dès qu'une mise à jour ou suppression a lieu dans la DB (Write-Through ou Cache-Aside strict). En cas de forte concurrence, on peut utiliser des "Distributed Locks" (ex: Redlock) ou la commande Redis `WATCH` pour les transactions afin d'éviter les "Race conditions" où une valeur obsolète écraserait le cache.

**3. Quand un TTL trop court est-il problématique ?**
Un TTL trop court force l'application à interroger la base de données principale de manière excessive car le cache expire rapidement. Cela annule les bénéfices de performance du cache, augmente la charge sur la base de données relationnelle et accroît la latence globale. Cela est particulièrement critique pour les données lourdes à calculer ou peu volatiles (ex: un catalogue produit).
