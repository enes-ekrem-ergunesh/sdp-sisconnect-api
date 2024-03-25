import config
import pymysql.cursors


def get_connection():
    connection = pymysql.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_DATABASE,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    return connection


def get_harmony_connection():
    connection = pymysql.connect(
        host=config.H_DB_HOST,
        port=config.H_DB_PORT,
        user=config.H_DB_USER,
        password=config.H_DB_PASSWORD,
        database=config.H_DB_DATABASE,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    return connection
