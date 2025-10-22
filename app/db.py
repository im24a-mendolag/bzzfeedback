import mysql.connector
from mysql.connector import pooling
from config import DB_CONFIG


class MySQLPool:
    _pool: pooling.MySQLConnectionPool | None = None

    @classmethod
    def init_pool(cls) -> None:
        if cls._pool is None:
            cls._pool = pooling.MySQLConnectionPool(
                pool_name="bzz_pool",
                pool_size=5,
                pool_reset_session=True,
                **DB_CONFIG,
            )

    @classmethod
    def get_connection(cls):
        if cls._pool is None:
            cls.init_pool()
        return cls._pool.get_connection()


def query_one(sql: str, params: tuple = ()):  # returns single row as dict
    conn = MySQLPool.get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        row = cur.fetchone()
        cur.close()
        return row
    finally:
        conn.close()


def query_all(sql: str, params: tuple = ()):  # returns list of dicts
    conn = MySQLPool.get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params)
        rows = cur.fetchall()
        cur.close()
        return rows
    finally:
        conn.close()


def execute(sql: str, params: tuple = ()) -> int:  # returns lastrowid
    conn = MySQLPool.get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        last_id = cur.lastrowid
        cur.close()
        return last_id
    finally:
        conn.close()

