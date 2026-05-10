"""
TP3 - Exercice 2 : Ingestion de données IoT
Use Case : SmartGrid DZ - 10 000 capteurs, 5 minutes de mesures
"""
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement, BatchType
import uuid
import random
from datetime import datetime, timedelta
import time

# Configuration
CASSANDRA_HOST = 'localhost'
KEYSPACE = 'smartgrid'
NB_CAPTEURS = 10000
MINUTES_HISTORIQUE = 5

WILAYAS = ["Alger", "Oran", "Constantine", "Annaba", "Blida"]
COMMUNES = {
    "Alger": ["Bab Ezzouar", "Hydra", "El Harrach", "Dar El Beida"],
    "Oran": ["Bir El Djir", "Es Senia", "Arzew"],
    "Constantine": ["El Khroub", "Ain Smara", "Hamma Bouziane"],
    "Annaba": ["El Bouni", "El Hadjar", "Seraidi"],
    "Blida": ["Bougara", "Boufarik", "Larbaa"],
}

def connect():
    """Connexion au cluster Cassandra"""
    cluster = Cluster([CASSANDRA_HOST])
    session = cluster.connect(KEYSPACE)
    return session, cluster


def generate_mesure(capteur_id, wilaya, commune, timestamp):
    """Générer une mesure réaliste pour un capteur"""
    tension_base = 220  # Volts (réseau algérien)
    
    return {
        "capteur_id": capteur_id,
        "date_jour": timestamp.date().isoformat(),
        "timestamp": timestamp,
        "wilaya": wilaya,
        "commune": commune,
        # Variation normale ± 10V
        "tension_v": round(tension_base + random.gauss(0, 5), 2),
        "courant_a": round(random.uniform(0.5, 15.0), 2),
        "puissance_kw": round(random.uniform(0.1, 3.3), 3),
        "frequence_hz": round(50 + random.gauss(0, 0.1), 2),
        "temperature": round(random.uniform(20, 65), 1),
        # 5% de chance d'alerte
        "alerte": random.random() < 0.05,
    }


def insert_single(session, mesure):
    query = """
        INSERT INTO mesures_par_capteur (capteur_id, date_jour, timestamp, wilaya, commune, tension_v, courant_a, puissance_kw, frequence_hz, temperature, alerte)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    prepared = session.prepare(query)
    session.execute(prepared, [
        mesure['capteur_id'], mesure['date_jour'], mesure['timestamp'],
        mesure['wilaya'], mesure['commune'], mesure['tension_v'], mesure['courant_a'],
        mesure['puissance_kw'], mesure['frequence_hz'], mesure['temperature'], mesure['alerte']
    ])


def insert_batch(session, mesures: list):
    query = """
        INSERT INTO mesures_par_capteur (capteur_id, date_jour, timestamp, wilaya, commune, tension_v, courant_a, puissance_kw, frequence_hz, temperature, alerte)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    prepared = session.prepare(query)
    
    # Division par capteur_id et date pour que toutes les requetes du batch tombent sur le même noeud (la même partition)
    # Dans Cassandra, UNLOGGED BATCH est efficace uniquement si toutes les écritures sont pour la MÊME partition (meme capteur_id)
    # Ici on simplifie avec des petits batch, mais idéalement on groupe par capteur_id
    
    for i in range(0, len(mesures), 50):
        batch = BatchStatement(batch_type=BatchType.UNLOGGED)
        for mesure in mesures[i:i+50]:
            batch.add(prepared, [
                mesure['capteur_id'], mesure['date_jour'], mesure['timestamp'],
                mesure['wilaya'], mesure['commune'], mesure['tension_v'], mesure['courant_a'],
                mesure['puissance_kw'], mesure['frequence_hz'], mesure['temperature'], mesure['alerte']
            ])
        session.execute(batch)


def run_ingestion(session):
    print(f"Démarrage ingestion : {NB_CAPTEURS} capteurs × {MINUTES_HISTORIQUE} min")
    start = time.time()
    
    capteurs = []
    for _ in range(NB_CAPTEURS):
        wilaya = random.choice(WILAYAS)
        commune = random.choice(COMMUNES[wilaya])
        capteurs.append({'id': uuid.uuid4(), 'wilaya': wilaya, 'commune': commune})
        
    now = datetime.now()
    all_mesures = []
    for m in range(MINUTES_HISTORIQUE):
        current_time = now - timedelta(minutes=m)
        for c in capteurs:
            mesure = generate_mesure(c['id'], c['wilaya'], c['commune'], current_time)
            all_mesures.append(mesure)
            
    insert_batch(session, all_mesures)
    
    elapsed = time.time() - start
    total = NB_CAPTEURS * MINUTES_HISTORIQUE
    print(f"\n✅ {total:,} mesures insérées en {elapsed:.1f}s")
    print(f"   Débit : {total/elapsed:,.0f} mesures/seconde")


if __name__ == "__main__":
    session, cluster = connect()
    run_ingestion(session)
    cluster.shutdown()
