import os
from psycopg_pool import ConnectionPool
from dotenv import load_dotenv

load_dotenv()

pool = None
conninfo=os.getenv('DATABASE_URL')
print(conninfo)
def get_pool():
    global pool
    if not pool:
        pool = ConnectionPool(conninfo)
    return pool