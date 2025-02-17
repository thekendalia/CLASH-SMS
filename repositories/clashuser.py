from repositories.db import get_pool
from psycopg.rows import dict_row
import bcrypt


def get_users_with_clan_tags():
    """
    Fetches users who have clan tags and phone numbers.
    """
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT 
                    clan_tag, phone 
                FROM 
                    users 
                WHERE 
                    clan_tag != '0' AND phone != '0'
                """
            )
            return cursor.fetchall()


def get_clash_users():
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """SELECT
                                clashname,
                                optin,
                                id 
                            FROM 
                                clash"""
            )
            return cursor.fetchall()
        
def get_id():
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """SELECT
                                id 
                            FROM 
                                clash"""
            )
            return cursor.fetchall()


def insert_clash_users(cname: str, opt: bool):
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            insert_query = """INSERT INTO clash (clashname, optin)
                              VALUES (%s, %s);"""
            cursor.execute(insert_query, (cname, opt))
            conn.commit()
            

def delete_clash_users(clashid: int):
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            delete_query = """DELETE FROM clash WHERE id = %s;"""
            cursor.execute(delete_query, (clashid,))
            conn.commit()
            
            
def new_account(uname: str, cname: str, password: str):
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            insert_query = """INSERT INTO users (username, email, password, code, clan_tag, phone)
                              VALUES (%s, %s, %s, 7685, 000, 0);"""
            cursor.execute(insert_query, (uname, cname, password))
            conn.commit()
            
def update_clan_tag(clan_tag: str, email: str, player_tag: str):  
    pool = get_pool() 
    with pool.connection() as conn:  
        with conn.cursor() as cursor:   
            update_query = """UPDATE users SET clan_tag = %s, clan = %s WHERE email = %s;"""  
            cursor.execute(update_query, (clan_tag, player_tag, email))
            conn.commit()
            
def delete_account(email: str):  
    pool = get_pool() 
    with pool.connection() as conn:  
        with conn.cursor() as cursor:   
            update_query = """DELETE FROM users where email = %s"""  
            cursor.execute(update_query, (email,))
            conn.commit()
            

def login_user(username: str, userpass: str):   
    pool = get_pool()  
    with pool.connection() as conn:  
        with conn.cursor() as cur: 
            cur.execute('SELECT id, username, email, password FROM users WHERE username = %s OR email = %s', (username, username))  
            user_record = cur.fetchone()  
            
            if user_record:  
                user_id, db_username, clash_name, hashed_password = user_record  
                
                user_bytes = userpass.encode('utf-8')  
                if bcrypt.checkpw(user_bytes, hashed_password.encode('utf-8')):  
                    return True, user_id, db_username, clash_name
            return False, None, None, 'Invalid username or password'
        
def user_data(email: str):   
    pool = get_pool()  
    with pool.connection() as conn:  
        with conn.cursor() as cur:   
            cur.execute('SELECT id, username, email, clan_tag, terms, phone FROM users WHERE email = %s', (email,))  
            user_record = cur.fetchone()  
            
            if user_record:  
                user_id, db_username, clash_name, clan_tag, terms, phone = user_record  
                
                return True, user_id, db_username, clash_name, clan_tag, terms, phone
            return False, None, None, 'Invalid username or password', None, None, None
        
def clan_tag():
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT username, clan_tag, phone FROM users WHERE clan_tag != %s',
                ('0',)
            )
            user_records = cur.fetchall()

            if user_records:
                # Create a list of dictionaries containing username, clan_tag, and phone
                user_data_list = [
                    {'username': record[0], 'clan_tag': record[1], 'phone': record[2]}
                    for record in user_records
                ]
                return user_data_list
            return []



            
def existingaccount(name: str) -> bool:
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT EXISTS(
                    SELECT 1
                    FROM users
                    WHERE LOWER(username) = %s
                )""",
                (name,)
            )
            exists = cursor.fetchone()[0]
            return exists
        
def existingemail(name: str) -> bool:
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT EXISTS(
                    SELECT 1
                    FROM users
                    WHERE LOWER(email) = %s
                )""",
                (name,)
            )
            exists = cursor.fetchone()[0]
            return exists
        
            
def existingemail(name: str) -> bool:
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT EXISTS(
                    SELECT 1
                    FROM users
                    WHERE LOWER(email) = %s
                )""",
                (name,)
            )
            exists = cursor.fetchone()[0]
            return exists


def check_user_exists(name: str) -> bool:
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT EXISTS(
                    SELECT 1
                    FROM clash
                    WHERE clashname = %s
                )""",
                (name,)
            )
            exists = cursor.fetchone()[0]
            return exists
            
            
def update_user_code(code: int, email: str):  
    pool = get_pool() 
    with pool.connection() as conn:  
        with conn.cursor() as cursor:   
            update_query = """UPDATE users SET code = %s WHERE email = %s;"""  
            cursor.execute(update_query, (code, email))
            conn.commit()
            
            
def check_code(email: str):  
    pool = get_pool()  
    with pool.connection() as conn:  
        with conn.cursor() as cursor:  
            cursor.execute(  
                """SELECT code FROM users WHERE email = %s""",
                (email,)  
            )  
            result = cursor.fetchone()
            return result[0]
            
def update_password(password: str, email: str):  
    pool = get_pool() 
    with pool.connection() as conn:  
        with conn.cursor() as cursor:   
            update_query = """UPDATE users SET password = %s WHERE email = %s;"""  
            cursor.execute(update_query, (password, email))
            conn.commit()
            
def update_term_status_true(email: str):  
    pool = get_pool() 
    with pool.connection() as conn:  
        with conn.cursor() as cursor:   
            update_query = """UPDATE users SET terms = true WHERE email = %s;"""  
            cursor.execute(update_query, (email,))
            conn.commit()
            
def update_term_status_false(email: str):  
    pool = get_pool() 
    with pool.connection() as conn:  
        with conn.cursor() as cursor:   
            update_query = """UPDATE users SET terms = false WHERE email = %s;"""  
            cursor.execute(update_query, (email,))
            conn.commit()
            
def update_phone(email: str, phone: str):  
    pool = get_pool() 
    with pool.connection() as conn:  
        with conn.cursor() as cursor:   
            update_query = """UPDATE users SET phone = %s WHERE email = %s;"""  
            cursor.execute(update_query, (phone, email))
            conn.commit()
            
def users():
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT * FROM USERS""",())
            exists = cursor.fetchall()
            return exists
        
def war_status():
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """SELECT id, clan, clan_tag, phone, username, enemy_clan
FROM USERS
WHERE clan_tag != '0' AND phone != '0' AND clan != '0' AND terms is true;""",())
            exists = cursor.fetchall()
            return exists


def update_enemy_clan(id: int, clan: str):  
    pool = get_pool() 
    with pool.connection() as conn:  
        with conn.cursor() as cursor:   
            update_query = """UPDATE users SET enemy_clan = %s WHERE id = %s;"""  
            cursor.execute(update_query, (clan, id))
            conn.commit()