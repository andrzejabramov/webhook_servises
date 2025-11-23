from asyncpg import Pool

from src.db.pools import get_write_pool

# Это — "точка инъекции" для FastAPI
def get_db_pool() -> Pool:
    """Для вебхуков → paydb"""
    return get_write_pool()
