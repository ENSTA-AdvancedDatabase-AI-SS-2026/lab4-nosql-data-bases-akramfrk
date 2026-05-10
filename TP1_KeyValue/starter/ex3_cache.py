"""
TP1 - Exercice 3 : Pattern Cache-Aside avec TTL
Use Case : Cache des pages produits ShopFast
"""
import redis
import json
import time
from typing import Optional

r = redis.Redis(host='localhost', port=6379, decode_responses=True)


def slow_db_get_product(product_id: int) -> Optional[dict]:
    """Simule une requête PostgreSQL lente (2 secondes)"""
    time.sleep(2)
    products = {
        1: {"id": 1, "name": "Samsung Galaxy A54", "price": 65000, "stock": 15},
        2: {"id": 2, "name": "Laptop HP 15-inch", "price": 120000, "stock": 8},
        3: {"id": 3, "name": "Casque JBL Bluetooth", "price": 12000, "stock": 50},
        4: {"id": 4, "name": "Clavier Mécanique", "price": 8000, "stock": 30},
    }
    return products.get(product_id)


def get_product_cached(r, product_id: int, ttl: int = 600) -> Optional[dict]:
    """
    Pattern Cache-Aside :
    1. Chercher dans Redis (clé: "product_cache:{product_id}")
    2. Si MISS → chercher dans slow_db → stocker dans Redis avec TTL
    3. Retourner le produit
    4. Afficher si c'est un HIT ou MISS avec la latence
    """
    start = time.time()
    key = f"product_cache:{product_id}"
    cached = r.get(key)
    
    if cached:
        elapsed = time.time() - start
        print(f"CACHE HIT ({elapsed*1000:.2f}ms)")
        return json.loads(cached)
        
    product = slow_db_get_product(product_id)
    if product:
        r.setex(key, ttl, json.dumps(product))
        
    elapsed = time.time() - start
    print(f"CACHE MISS ({elapsed*1000:.2f}ms)")
    return product


def invalidate_product_cache(r, product_id: int):
    """Supprimer le cache d'un produit (après mise à jour en DB)"""
    r.delete(f"product_cache:{product_id}")


def benchmark_cache(r, product_id: int, iterations: int = 20):
    """
    Effectuer 'iterations' appels à get_product_cached
    Afficher :
    - Temps moyen cache HIT
    - Temps moyen cache MISS
    - Taux de cache hit (%)
    """
    invalidate_product_cache(r, product_id)
    
    hit_times = []
    miss_times = []
    
    for i in range(iterations):
        start = time.time()
        get_product_cached(r, product_id)
        elapsed = time.time() - start
        
        if i == 0:
            miss_times.append(elapsed)
        else:
            hit_times.append(elapsed)
            
    hit_avg = sum(hit_times) / len(hit_times) if hit_times else 0
    miss_avg = sum(miss_times) / len(miss_times) if miss_times else 0
    hit_rate = (len(hit_times) / iterations) * 100
    
    print(f"Temps moyen cache HIT: {hit_avg*1000:.2f}ms")
    print(f"Temps moyen cache MISS: {miss_avg*1000:.2f}ms")
    print(f"Taux de cache hit: {hit_rate:.2f}%")


if __name__ == "__main__":
    r.flushdb()
    
    print("=== Test Cache-Aside ===")
    print("\nPremier appel (MISS attendu):")
    get_product_cached(r, 1)
    
    print("\nDeuxième appel (HIT attendu):")
    get_product_cached(r, 1)
    
    print("\n=== Benchmark ===")
    benchmark_cache(r, 1, iterations=10)
