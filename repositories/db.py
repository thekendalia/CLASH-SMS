import os
from psycopg_pool import ConnectionPool

pool = None
conninfo=os.getenv('DATABASE_URL')
def get_pool():
    global pool
    if not pool:
        pool = ConnectionPool(conninfo)
    return pool