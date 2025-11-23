from asyncpg import Pool

from src.db.pools import get_write_pool, get_read_pool


def get_write_db_pool() -> Pool:
    return get_write_pool()

def get_read_db_pool() -> Pool:
    return get_read_pool()