import pymysql
import db.dbConnections as db
from helpers.http_response import http_response


def get_registered_users():
    """
    Retrieves all the registered users
    """
    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                select u.id as user_id,
                       p.id as personnel_id,
                       s.id as student_id
                from users u
                left join personnels p on u.id = p.user_id
                left join students s on u.id = s.user_id
                """
                cursor.execute(sql)
                return cursor.fetchall()
    except pymysql.MySQLError as e:
        db.http_response(500, "Internal Server Error: " + str(e))


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


def get_user_by_email(email):
    """
    Retrieves a user by email from the sisconnect database
    """

    connection = db.get_connection()
    try:
        with connection:
            with connection.cursor() as cursor:
                sql = """
                select *
                from users u
                join personnels p on u.id = p.user_id
                where u.email = %s;
                """
                cursor.execute(sql, email)
                result = cursor.fetchone()
                if result:
                    return result
                else:
                    sql = """
                    select *
                    from users u
                    join students s on u.id = s.user_id
                    where u.email = %s;
                    """
                    cursor.execute(sql, email)
                    result = cursor.fetchone()
                    return result
    except pymysql.MySQLError:
        http_response(500, "An error occurred while getting the user credentials from database.")


def get_user_by_id_sc(user_id):
    """
    Get a user by id

    Args:
    user_id (int): the id of the user

    Returns:
    dict: user data
    """

    # get a connection to the database (sisConnect)
    connection = db.get_connection()
    try:  # try to get the user by id
        with connection:  # use the connection
            with connection.cursor() as cursor:  # get a cursor
                # get user as personnel
                sql = """
                select *
                from users u
                join personnels p on u.id = p.user_id
                where u.id = %s;
                """  # SQL query to get the user by id
                cursor.execute(sql, user_id)  # execute the query
                result = cursor.fetchone()  # get the result
                if result:  # if the result is not None, return the result
                    return result
                else:  # if the result is None, get user as student
                    sql = """
                    select *
                    from users u
                    join students s on u.id = s.user_id
                    where u.id = %s;
                    """  # SQL query to get the user by id
                    cursor.execute(sql, user_id)  # execute the query
                    result = cursor.fetchone()  # get the result
                    return result
    except pymysql.MySQLError:  # handle exceptions
        http_response(500, "An error occurred while getting the user credentials from database.")


def insert_user(user):
    """
    Inserts a user into the sisConnect database

    Args:
    user: dict
    """
    insert_user_as_user(user)  # Insert the user into the user table
    insert_user_as_personnel_or_student(user)  # Insert the user into the personnel or student table

    user["public_profile_id"] = create_public_profile(user["user_id"])  # create a public profile for the user
    user["administrative_profile_id"] = create_administrative_profile(
        user["user_id"])  # create an administrative profile for the user


def insert_user_about_fields(user):
    """
    Inserts the user about fields into the database

    Args:
    user: dict
    """
    is_personnel = False
    if "personnel_id" in user:
        is_personnel = True
    connection = db.get_connection()  # get a connection to the database (sisConnect)
    try:  # try to insert the user about fields
        with connection:  # use the connection
            with connection.cursor() as cursor:  # get a cursor
                # SQL query to insert the user about fields
                sql = (f"""
                    insert into profile_field_data (profile_id, profile_field_type_id, data)
                    values 
                        ({user["public_profile_id"]}, 15, %s),
                        ({user["public_profile_id"]}, 13, %s),
                        ({user["public_profile_id"]}, 6, %s),
                        ({user["public_profile_id"]}, 14, %s);
                """)
                cursor.execute(
                    sql,
                    (
                        user["school_email"] if is_personnel else user["email"],
                        user["gender"],
                        user["birthdate"],
                        None if is_personnel else user["address"]
                    )
                )  # execute the query
            connection.commit()  # commit the changes
            delete_null_about_fields()
    except pymysql.MySQLError as e:  # handle exceptions
        http_response(500, "Database server error: " + str(e))


def insert_user_as_user(user):
    """
    Insert the user into the user table in the sisConnect database

    Args:
        user: dict
    """
    connection = db.get_connection()  # get a connection to the database (sisConnect)
    try:  # try to insert the user
        with connection:  # use the connection
            with connection.cursor() as cursor:  # get a cursor
                # SQL query to insert the user
                sql = "INSERT INTO `users` (`email`) VALUES (%s)"
                cursor.execute(sql, (user["email"],))  # execute the query
                connection.commit()  # commit the changes
                # get the id of the user
                user["user_id"] = cursor.lastrowid
    except pymysql.MySQLError as e:  # handle exceptions
        http_response(500, "Database server error: " + str(e))


def insert_user_as_personnel_or_student(user):
    """
    Insert the user into the personnel or student table in the sisConnect database

    Args:
        user: dict
    """
    connection = db.get_connection()  # get a connection to the database (sisConnect)
    try:  # try to insert the user
        with connection:  # use the connection
            with connection.cursor() as cursor:  # get a cursor
                if user["table"] == "personnels":
                    # SQL query to insert the user
                    sql = "INSERT INTO `personnels` (`id`, `user_id`) VALUES (%s, %s)"
                    cursor.execute(sql, (user["id"], user["user_id"]))  # execute the query
                    connection.commit()
                elif user["table"] == "students":
                    # SQL query to insert the user
                    sql = "INSERT INTO `students` (`id`, `user_id`) VALUES (%s, %s)"
                    cursor.execute(sql, (user["id"], user["user_id"]))
                    connection.commit()
    except pymysql.MySQLError as e:  # handle exceptions
        http_response(500, "Database server error: " + str(e))


def insert_token(token, user_id, valid_until):
    """
    Inserts a token into the database

    Args:
    token: str
    user_id: int
    valid_until: datetime
    """
    # get a connection to the database (sisConnect)
    connection = db.get_connection()
    try:  # try to insert the token
        with connection:  # use the connection
            with connection.cursor() as cursor:  # get a cursor
                # SQL query to insert the token
                sql = "INSERT INTO `tokens` (`token`, `user_id`, `valid_until`) VALUES (%s, %s, %s)"
                cursor.execute(sql, (token, user_id, valid_until))  # execute the query
                connection.commit()  # commit the changes
    except pymysql.MySQLError as e:  # handle exceptions
        http_response(500, "Database server error: " + str(e))


def append_user_fields(user, email):
    """
    Get the user fields from the sisConnect database and append them to the user

    Args:
    user: dict
    """
    user_sc = get_user_by_email(email)
    # append all the fields from user_sc to user
    for key in user_sc:
        user[key] = user_sc[key]
    # remove unnecessary user_id field
    user.pop("user_id")


def revoke_token(token, user_id):
    """
    Revokes a token
    """
    connection = db.get_connection()  # get a connection to the database (sisConnect)
    try:  # try to revoke the token
        with connection:  # use the connection
            with connection.cursor() as cursor:  # get a cursor
                # SQL query to revoke the token
                sql = "update tokens set revoked_at = NOW() where token = %s and user_id = %s"
                cursor.execute(sql, (token, user_id))  # execute the query
                connection.commit()
                return {
                    "message": "Logged out successfully."
                }
    except pymysql.MySQLError as e:  # handle exceptions
        http_response(500, "Database server error: " + str(e))


def create_public_profile(user_id):
    """
    Creates a public profile for the user

    Args:
    user_id: int
    """
    connection = db.get_connection()  # get a connection to the database (sisConnect)
    try:  # try to create a public profile
        with connection:  # use the connection
            with connection.cursor() as cursor:  # get a cursor
                # SQL query to create a public profile
                sql = ("insert into profiles (user_id, profile_type_id, visibility_set_id)"
                       "values (%s, 1, 1);")
                cursor.execute(sql, (user_id,))  # execute the query
                last_id = cursor.lastrowid
                connection.commit()  # commit the changes
                return last_id
    except pymysql.MySQLError as e:  # handle exceptions
        http_response(500, "Database server error: " + str(e))


def create_administrative_profile(user_id):
    """
    Creates an administrative profile for the user.

    profile_type_id: 2 (administration view)
    visibility_set_id: 3 (admin only)

    Args:
    user_id: int
    """
    connection = db.get_connection()  # get a connection to the database (sisConnect)
    try:  # try to create an administrative profile
        with connection:  # use the connection
            with connection.cursor() as cursor:  # get a cursor
                # SQL query to create a administrative profile
                sql = ("insert into profiles (user_id, profile_type_id, visibility_set_id)"
                       "values (%s, 2, 3);")
                cursor.execute(sql, (user_id,))  # execute the query
                last_id = cursor.lastrowid
                connection.commit()  # commit the changes
                return last_id
    except pymysql.MySQLError as e:  # handle exceptions
        http_response(500, "Database server error: " + str(e))


def delete_null_about_fields():
    """
    Deletes the null about fields from the database
    """
    connection = db.get_connection()  # get a connection to the database (sisConnect)
    try:  # try to delete the null about fields
        with connection:  # use the connection
            with connection.cursor() as cursor:  # get a cursor
                # SQL query to delete the null about fields
                sql = "delete from profile_field_data where data is null or data = '';"
                cursor.execute(sql)  # execute the query
                connection.commit()  # commit the changes
    except pymysql.MySQLError as e:  # handle exceptions
        http_response(500, "Database server error: " + str(e))
