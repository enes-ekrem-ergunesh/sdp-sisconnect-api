from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_DATABASE
import pymysql.cursors


def get_connection():
    connection = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_DATABASE,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    return connection
