"""
TP1 - Exercice 2 : Sessions utilisateur
Use Case : Gestion des sessions ShopFast
"""
import redis
import uuid
from typing import Optional

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def create_session(r, user_id: str) -> str:
    """
    Créer une session avec TTL 30 minutes.
    Retourne l'ID de la session.
    """
    session_id = str(uuid.uuid4())
    r.setex(f"session:{session_id}", 1800, user_id)
    return session_id

def get_session_user(r, session_id: str) -> Optional[str]:
    """
    Récupérer l'utilisateur d'une session et renouveler le TTL (sliding expiration).
    """
    key = f"session:{session_id}"
    user_id = r.get(key)
    if user_id:
        r.expire(key, 1800)
    return user_id

def delete_session(r, session_id: str):
    """
    Supprimer une session.
    """
    r.delete(f"session:{session_id}")
