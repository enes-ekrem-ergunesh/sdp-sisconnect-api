import pymysql
import db.dbConnections as db
from helpers.http_response import http_response


def get_all_posts():
    """
    Get all posts
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                select * 
                from posts
                where deleted_at is null;
                ;
                """
                cursor.execute(sql)
                return cursor.fetchall()
    except pymysql.MySQLError as e:
        http_response(500, "Internal Server Error: " + str(e))


def get_posts_by_user_id(user_id):
    """
    Get all posts by user id
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                select * 
                from posts 
                where user_id = %s
                and deleted_at is null;
                ;
                """
                cursor.execute(sql, (user_id,))
                return cursor.fetchall()
    except pymysql.MySQLError as e:
        http_response(500, "Internal Server Error: " + str(e))


def get_post_by_id(post_id):
    """
    Get post by id
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                select * 
                from posts 
                where id = %s
                and deleted_at is null
                ;
                """
                cursor.execute(sql, (post_id,))
                return cursor.fetchone()
    except pymysql.MySQLError as e:
        http_response(500, "Internal Server Error: " + str(e))


def get_all_posts_of_connections(user_id):
    """
    Get all posts of connections
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                select p.*
                from posts p
                join connections c on p.user_id = c.connected_user_id
                where c.user_id = %s
                and c.accepted_at is not null
                and c.blocked = 0
                and c.deleted_at is null
                and p.deleted_at is null
                order by p.created_at desc;
                ;
                """
                cursor.execute(sql, (user_id,))
                return cursor.fetchall()
    except pymysql.MySQLError as e:
        http_response(500, "Internal Server Error: " + str(e))


def create_post(user_id, post):
    """
    Create a post
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                insert into posts (user_id, content)
                values (%s, %s);
                """
                cursor.execute(sql, (user_id, post["content"]))
                connection.commit()
                return cursor.lastrowid
    except pymysql.MySQLError as e:
        http_response(500, "Internal Server Error: " + str(e))


def soft_delete_post(user_id, post_id):
    """
    Soft delete a post
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                update posts
                set deleted_at = now()
                where id = %s
                and user_id = %s;
                """
                cursor.execute(sql, (post_id, user_id))
                connection.commit()
                return cursor.lastrowid
    except pymysql.MySQLError as e:
        http_response(500, "Internal Server Error: " + str(e))
