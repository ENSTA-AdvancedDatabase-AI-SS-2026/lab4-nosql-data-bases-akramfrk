"""
TP1 - Exercice 5 : Pipeline & Transactions
Use Case : ShopFast Bulk Insert and Orders
"""
import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def bulk_insert_products(r, products: dict):
    """
    Insérer plusieurs produits avec un pipeline.
    products = {product_id: product_data_dict}
    """
    pipeline = r.pipeline()
    for pid, data in products.items():
        pipeline.hset(f"product:{pid}", mapping=data)
    pipeline.execute()

def process_order(r, order_id: str, user_id: str, total_amount: float):
    """
    Transaction MULTI/EXEC :
    1. Ajouter la commande à l'historique du user
    2. Vider le panier du user
    """
    pipeline = r.pipeline(transaction=True)
    pipeline.lpush(f"orders:{user_id}", order_id)
    pipeline.delete(f"cart:{user_id}")
    pipeline.execute()
