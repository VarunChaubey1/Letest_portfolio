from psycopg2.pool import SimpleConnectionPool
from config import *

pool = SimpleConnectionPool(
    1,
    20,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

def get_connection():
    return pool.getconn()

def release_connection(conn):
    pool.putconn(conn)