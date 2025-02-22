import os  
from psycopg_pool import ConnectionPool  
from dotenv import load_dotenv  

load_dotenv()  

# Load connection info from environment variable  
conninfo = os.getenv('DATABASE_URL')  

# Initialize connection pool  
pool = ConnectionPool(conninfo, min_size=1, max_size=20)  # Set min and max sizes  

def get_pool():  
    global pool  
    if not pool:  
        pool = ConnectionPool(conninfo)  
    return pool  

def execute_query(query, params=None):  
    pool = get_pool()  
    try:  
        with pool.connection() as conn:  # Automatically handles closing the connection  
            with conn.cursor() as cursor:  
                cursor.execute(query, params)  
                return cursor.fetchall()  # Return results as needed  
    except Exception as e:  
        print(f"Database query error: {e}")  
        # Handle or raise exception as needed