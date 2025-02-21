import os  
import time  
from psycopg_pool import ConnectionPool  
from psycopg import OperationalError  # Import the OperationalError  

pool = None  

def get_pool():  
    global pool  
    if pool is None:  
        db_url = os.getenv('DATABASE_URL', '')  
        if not db_url:  
            raise ValueError("DATABASE_URL environment variable is not set.")  
        
        # Create the connection pool with optional parameters  
        pool = ConnectionPool(  
            conninfo=db_url,  
            min_size=1,  # Minimum number of connections  
            max_size=30,  # Adjust based on your needs  
            max_lifetime=45  # Optional: Max lifetime of connections in seconds  
        )  
    return pool  

def get_connection():  
    retries = 5  
    for attempt in range(retries):  
        try:  
            return get_pool().getconn()  
        except OperationalError as e:  # Catch OperationalError  
            print(f"Attempt {attempt + 1} to get a connection failed: {e}")  
            if attempt < retries - 1:  
                time.sleep(2)  # Wait before retrying  
            else:  
                raise  

def close_pool():  
    global pool  
    if pool is not None:  
        pool.closeall()  # Close all connections in the pool  
        pool = None