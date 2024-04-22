import db.dbConnections as db


def get_profile_about_by_id(profile_id, user_id):
    """
    Retrieves a profile about by id
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                select pft.name, pfd.data, pft.data_type
                from profiles p
                join users u on p.user_id = u.id
                join profile_field_data pfd on p.id = pfd.profile_id
                join profile_field_types pft on pfd.profile_field_type_id = pft.id
                where p.id = %s
                and u.id = %s
                ;
                """
                cursor.execute(sql, (profile_id, user_id,))
                return cursor.fetchall()
    except db.pymysql.MySQLError as e:
        db.http_response(500, "Internal Server Error: " + str(e))


def get_profile_id_by_user_id(user_id):
    """
    Retrieves a profile id by user id
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                select id
                from profiles
                where user_id = %s
                ;
                """
                cursor.execute(sql, (user_id,))
                return cursor.fetchone()
    except db.pymysql.MySQLError as e:
        db.http_response(500, "Internal Server Error: " + str(e))


def get_profile_field_types():
    """
    Retrieves profile field types
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                select *
                from profile_field_types
                ;
                """
                cursor.execute(sql)
                return cursor.fetchall()
    except db.pymysql.MySQLError as e:
        db.http_response(500, "Internal Server Error: " + str(e))
