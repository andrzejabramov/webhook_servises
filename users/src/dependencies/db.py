from asyncpg import Pool

from src.db.pools import get_accounts_db_pool


def get_accounts_db_pool_dep() -> Pool:  # ← новая зависимость
    """Для учётных записей → mydb"""
    return get_accounts_db_pool()