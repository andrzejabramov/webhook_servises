from asyncpg import Pool

from src.db.pools import get_main_db_pool

# Это — "точка инъекции" для FastAPI
def get_db_pool() -> Pool:
    return get_main_db_pool()