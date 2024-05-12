import pymysql
import db.dbConnections as db
from helpers.http_response import http_response


def get_all_connections():
    """
    Get all connections
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                select * 
                from connections
                where deleted_at is null;
                ;
                """
                cursor.execute(sql)
                return cursor.fetchall()
    except pymysql.MySQLError as e:
        http_response(500, "Internal Server Error: " + str(e))


def get_connections_by_user_id(user_id):
    """
    Get all connections by user id
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                select * 
                from connections 
                where user_id = %s
                and deleted_at is null;
                ;
                """
                cursor.execute(sql, (user_id,))
                return cursor.fetchall()
    except pymysql.MySQLError as e:
        http_response(500, "Internal Server Error: " + str(e))


def get_connection_by_id(connection_id):
    """
    Get connection by id
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                select * 
                from connections 
                where id = %s
                and deleted_at is null
                ;
                """
                cursor.execute(sql, (connection_id,))
                return cursor.fetchone()
    except pymysql.MySQLError as e:
        http_response(500, "Internal Server Error: " + str(e))


def get_connection_between_users(user_id, other_user_id):
    """
    Get connection between two users
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                select * 
                from connections 
                where user_id = %s 
                and connected_user_id = %s
                and deleted_at is null
                ;
                """
                cursor.execute(sql, (user_id, other_user_id))
                return cursor.fetchone()
    except pymysql.MySQLError as e:
        http_response(500, "Internal Server Error: " + str(e))


def get_connection_requests(user_id):
    """
    Get connection requests
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                select c.user_id, c.created_at as 'request_time', c.id as 'connection_id', u.email
                from connections c
                join sisconnect.users u on c.user_id = u.id
                where c.connected_user_id = %s
                and c.accepted_at is null
                and c.deleted_at is null
                order by c.created_at desc;
                ;
                """
                cursor.execute(sql, (user_id,))
                return cursor.fetchall()
    except pymysql.MySQLError as e:
        http_response(500, "Internal Server Error: " + str(e))


def create_connection(user_id, connected_user_id):
    """
    Create a connection
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                insert into connections (user_id, connected_user_id, blocked) 
                values (%s, %s, 0);
                """
                cursor.execute(sql, (user_id, connected_user_id))
                connection.commit()
                return cursor.lastrowid
    except pymysql.MySQLError as e:
        http_response(500, "Internal Server Error: " + str(e))


def update_connection(_connection):
    """
    Update a connection
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                update connections
                set blocked = %s
                where id = %s;
                """
                cursor.execute(sql, (_connection["blocked"], _connection["id"]))
                connection.commit()
                return cursor.lastrowid
    except pymysql.MySQLError as e:
        http_response(500, "Internal Server Error: " + str(e))


def soft_delete_connection(user_id, connection_id):
    """
    Soft delete a connection
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                update connections
                set deleted_at = now()
                where id = %s
                and user_id = %s;
                """
                cursor.execute(sql, (connection_id, user_id))
                connection.commit()
                return cursor.lastrowid
    except pymysql.MySQLError as e:
        http_response(500, "Internal Server Error: " + str(e))


def soft_delete_connection_between_users(user_id, other_user_id):
    """
    Soft delete a connection between two users
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                update connections
                set deleted_at = now()
                where (user_id = %s and connected_user_id = %s)
                or (user_id = %s and connected_user_id = %s)
                ;
                """
                print(sql, user_id, other_user_id, other_user_id, user_id)
                cursor.execute(sql, (user_id, other_user_id, other_user_id, user_id))
                connection.commit()
                return cursor.lastrowid
    except pymysql.MySQLError as e:
        http_response(500, "Internal Server Error: " + str(e))


def accept_connection(_connection):
    """
    Accept a connection
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                update connections
                set accepted_at = now()
                where id = %s;
                """
                cursor.execute(sql, (_connection["id"],))
                connection.commit()

                sql = """
                insert into connections (user_id, connected_user_id, accepted_at, blocked)
                values (%s, %s, now(), 0);
                """
                cursor.execute(sql, (_connection["connected_user_id"], _connection["user_id"]))
                connection.commit()
    except pymysql.MySQLError as e:
        http_response(500, "Internal Server Error: " + str(e))
