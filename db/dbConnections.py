import config
import pymysql.cursors
from helpers.http_response import http_response

no_connection_message = 'Cannot connect to the database! Please try again later.'


def get_connection():
    try:
        connection = pymysql.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_DATABASE,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
    except pymysql.MySQLError:
        http_response(500, no_connection_message)

    return connection


def get_harmony_connection():
    try:
        connection = pymysql.connect(
            host=config.H_DB_HOST,
            port=config.H_DB_PORT,
            user=config.H_DB_USER,
            password=config.H_DB_PASSWORD,
            database=config.H_DB_DATABASE,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
    except pymysql.MySQLError:
        http_response(500, no_connection_message)
    return connection
