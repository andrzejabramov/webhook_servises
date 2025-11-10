from asyncpg import Pool

from webhook_json.src.db.pools import get_main_db_pool, get_accounts_db_pool

# Это — "точка инъекции" для FastAPI
def get_db_pool() -> Pool:
    """Для вебхуков → paydb"""
    return get_main_db_pool()

def get_accounts_db_pool_dep() -> Pool:  # ← новая зависимость
    """Для учётных записей → mydb"""
    return get_accounts_db_pool()