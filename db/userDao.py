import db.dbConnections as db


def get_user_by_id(user_id):
    """
    Retrieves a user by user id
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                select * from users where id = %s
                """
                cursor.execute(sql, (user_id,))
                return cursor.fetchone()
    except db.pymysql.MySQLError as e:
        db.http_response(500, "Internal Server Error: " + str(e))
