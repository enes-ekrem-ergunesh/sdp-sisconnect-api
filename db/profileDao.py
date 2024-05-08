import db.dbConnections as db


def get_profile_about_fields_by_profile_id(profile_id):
    """
    Retrieves profile about fields by profile id
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                select pfd.*,
                    pft.name as profile_field_type_name,
                    pft.data_type as profile_field_type_data_type
                from profile_field_data pfd
                join profile_field_types pft on pfd.profile_field_type_id = pft.id
                where pfd.profile_id = %s
                and pfd.deleted_at is null
                ;
                """
                cursor.execute(sql, (profile_id,))
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
                order by name
                ;
                """
                cursor.execute(sql)
                return cursor.fetchall()
    except db.pymysql.MySQLError as e:
        db.http_response(500, "Internal Server Error: " + str(e))


def get_empty_profile_field_types_by_profile_id(profile_id):
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
                where id not in (select pft.id
                                 from profile_field_types pft
                                          join profile_field_data pfd on pft.id = pfd.profile_field_type_id
                                 where pfd.profile_id = %s
                                   and pfd.deleted_at is null
                                   and pfd.data is not null
                                   )
                ;
                """
                cursor.execute(sql, (profile_id,))
                return cursor.fetchall()
    except db.pymysql.MySQLError as e:
        db.http_response(500, "Internal Server Error: " + str(e))


def update_profile_about_fields(profile_about_fields, user_id):
    """
    Updates the user profile about fields
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                update profile_field_data pfd
                set pfd.data = %s, pfd.deleted_at = %s
                where pfd.id = %s
                  and (select u.id
                       from users u
                                join profiles p on u.id = p.user_id
                       where p.id = pfd.profile_id) = %s
                ;
                """
                for profile_field in profile_about_fields:
                    if profile_field["id"] < 0 and not profile_field["deleted_at"]:
                        insert_profile_about_fields(profile_field, user_id)
                    else:
                        cursor.execute(
                            sql,
                            (profile_field["data"], profile_field["deleted_at"], profile_field["id"], user_id)
                        )
                connection.commit()
    except db.pymysql.MySQLError as e:
        db.http_response(500, "Internal Server Error: " + str(e))


def insert_profile_about_fields(profile_about_field, user_id):
    """
    Inserts the user profile about fields
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                insert into profile_field_data (profile_id, profile_field_type_id, data)
                values ((select p.id
                         from profiles p
                         where p.user_id = %s
                           and p.id = %s),
                        %s,
                        %s)
                ;
                """
                cursor.execute(
                    sql,
                    (
                        user_id,
                        profile_about_field["profile_id"],
                        profile_about_field["profile_field_type_id"],
                        profile_about_field["data"]
                    )
                )
                connection.commit()
    except db.pymysql.MySQLError as e:
        db.http_response(500, "Internal Server Error: " + str(e))
