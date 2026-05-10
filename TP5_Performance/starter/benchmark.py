"""
TP5 - Benchmark Comparatif NoSQL
Mesurer les performances de Redis, MongoDB, Cassandra, Neo4j
"""
import time
import statistics
import json
from typing import Callable, List, Tuple
import redis
from pymongo import MongoClient
from cassandra.cluster import Cluster
import threading

# ─── Utilitaires de mesure ────────────────────────────────────────────────────

def measure_latency(fn: Callable, iterations: int = 1000) -> dict:
    """
    Exécuter fn iterations fois et retourner les statistiques
    """
    latencies = []
    for _ in range(iterations):
        start = time.perf_counter()
        fn()
        latencies.append((time.perf_counter() - start) * 1000)  # en ms
    
    latencies.sort()
    return {
        "mean_ms": statistics.mean(latencies),
        "p50_ms": latencies[int(0.50 * len(latencies))],
        "p95_ms": latencies[int(0.95 * len(latencies))],
        "p99_ms": latencies[int(0.99 * len(latencies))],
        "max_ms": max(latencies),
        "throughput_rps": 1000 / statistics.mean(latencies)
    }


def print_results(name: str, results: dict):
    print(f"\n{'='*50}")
    print(f" {name}")
    print(f"{'='*50}")
    for k, v in results.items():
        print(f"  {k:20s}: {v:.2f}")


# ─── Ex1 : Benchmark Écriture ─────────────────────────────────────────────────

def benchmark_write_redis(n: int = 100_000):
    """Insérer n enregistrements dans Redis et mesurer le débit"""
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.flushdb()
        pipe = r.pipeline(transaction=False)
        start = time.perf_counter()
        for i in range(n):
            pipe.hset(f"bench:{i}", mapping={"val": i, "data": "X"*100})
            if i % 10000 == 0:
                pipe.execute()
        pipe.execute()
        elapsed = time.perf_counter() - start
        print(f"  Redis Write    : {n/elapsed:,.0f} ops/sec ({elapsed:.2f}s)")
    except Exception as e:
        print(f"  Redis Write    : Error - {e}")


def benchmark_write_mongodb(n: int = 100_000):
    """Insérer n documents dans MongoDB et mesurer le débit"""
    try:
        client = MongoClient("mongodb://admin:admin123@localhost:27017/")
        db = client["benchmark"]
        coll = db["bench"]
        coll.drop()
        start = time.perf_counter()
        docs = []
        for i in range(n):
            docs.append({"_id": i, "val": i, "data": "X"*100})
            if len(docs) >= 10000:
                coll.insert_many(docs, ordered=False)
                docs = []
        if docs:
            coll.insert_many(docs, ordered=False)
        elapsed = time.perf_counter() - start
        print(f"  MongoDB Write  : {n/elapsed:,.0f} ops/sec ({elapsed:.2f}s)")
    except Exception as e:
        print(f"  MongoDB Write  : Error - {e}")


def benchmark_write_cassandra(n: int = 100_000):
    """Insérer n rows dans Cassandra et mesurer le débit"""
    try:
        cluster = Cluster(['localhost'])
        session = cluster.connect()
        session.execute("CREATE KEYSPACE IF NOT EXISTS benchmark WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}")
        session.set_keyspace('benchmark')
        session.execute("DROP TABLE IF EXISTS bench")
        session.execute("CREATE TABLE bench (id int PRIMARY KEY, val int, data text)")
        
        from cassandra.query import BatchStatement, BatchType
        prepared = session.prepare("INSERT INTO bench (id, val, data) VALUES (?, ?, ?)")
        start = time.perf_counter()
        
        batch_size = 1000
        for i in range(0, n, batch_size):
            batch = BatchStatement(batch_type=BatchType.UNLOGGED)
            for j in range(i, min(i + batch_size, n)):
                batch.add(prepared, (j, j, "X"*100))
            session.execute(batch)
            
        elapsed = time.perf_counter() - start
        print(f"  Cassandra Write: {n/elapsed:,.0f} ops/sec ({elapsed:.2f}s)")
        cluster.shutdown()
    except Exception as e:
        print(f"  Cassandra Write: Error - {e}")


# ─── Ex2 : Benchmark Lecture ─────────────────────────────────────────────────

def benchmark_read_redis():
    """Point lookup, range (ZRANGE), complex (pipeline multi-get)"""
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        def point_lookup():
            r.hgetall("bench:5000")
        res = measure_latency(point_lookup, 1000)
        print_results("Redis Point Lookup", res)
    except Exception as e:
        print(f"Redis Read Error: {e}")


def benchmark_read_mongodb():
    """find_one, find avec range, aggregate pipeline"""
    try:
        client = MongoClient("mongodb://admin:admin123@localhost:27017/")
        coll = client["benchmark"]["bench"]
        def point_lookup():
            coll.find_one({"_id": 5000})
        res = measure_latency(point_lookup, 1000)
        print_results("MongoDB Point Lookup", res)
    except Exception as e:
        print(f"MongoDB Read Error: {e}")


# ─── Ex3 : Charge concurrente ─────────────────────────────────────────────────

def benchmark_concurrent(db_fn: Callable, n_clients: int = 50, requests_per_client: int = 200):
    """
    Lancer n_clients threads simultanés
    Chaque thread effectue requests_per_client requêtes
    Mesurer les latences globales et la dégradation vs single client
    """
    threads = []
    start = time.perf_counter()
    for _ in range(n_clients):
        t = threading.Thread(target=lambda: [db_fn() for _ in range(requests_per_client)])
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    elapsed = time.perf_counter() - start
    total_reqs = n_clients * requests_per_client
    print(f"  Concurrent : {total_reqs/elapsed:,.0f} req/sec ({elapsed:.2f}s)")


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("🚀 Benchmark NoSQL - Comparatif des 4 technologies")
    print("="*60)
    
    N = 10_000  # Réduire pour les tests, 100_000 pour la production
    
    print(f"\n📝 Benchmark Écriture ({N:,} enregistrements)")
    benchmark_write_redis(N)
    benchmark_write_mongodb(N)
    benchmark_write_cassandra(N)
    
    print(f"\n📖 Benchmark Lecture (1,000 requêtes)")
    benchmark_read_redis()
    benchmark_read_mongodb()
    
    print(f"\n⚡ Test Charge Concurrente (50 clients)")
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        def redis_task(): r.hgetall("bench:5000")
        print("  Testing Redis under load...")
        benchmark_concurrent(redis_task, 50, 200)
    except Exception as e:
         print(f"Error concurrent Redis: {e}")
         
    try:
        client = MongoClient("mongodb://admin:admin123@localhost:27017/")
        coll = client["benchmark"]["bench"]
        def mongo_task(): coll.find_one({"_id": 5000})
        print("  Testing MongoDB under load...")
        benchmark_concurrent(mongo_task, 50, 200)
    except Exception as e:
         print(f"Error concurrent MongoDB: {e}")
    
    print("\n✅ Benchmark terminé ! Consultez RAPPORT.md pour l'analyse.")
