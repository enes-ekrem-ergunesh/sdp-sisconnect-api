import pymysql
import db.dbConnections as db
from helpers.http_response import http_response


def append_user_fields(user):
    """
    Get the user fields from the harmony database and append them to the user

    Args:
    user: dict
    """
    user_h = get_user_by_email(user["email"])
    # append all the fields from user_h to user if not already present
    for key in user_h:
        if key not in user:
            user[key] = user_h[key]
    # remove unnecessary user_id field
    if "user_id" in user:
        user.pop("user_id")


def get_user_by_email(email):
    """
    Search user by email in the personnel's and students tables in the harmony database

    Args:
    email (str): the email of the user

    Returns:
    dict: user data
    """

    # get a connection to the database (harmony)
    connection = db.get_harmony_connection()
    try:  # try to search the user by email
        with connection:  # use the connection
            with connection.cursor() as cursor:  # get a cursor
                sql = """
                select *
                from personnels
                where school_email = %s;
                """  # SQL query to search the user by email
                cursor.execute(sql, email)  # execute the query
                result = cursor.fetchone()  # get the result
                if result:
                    # add table name to the result
                    result["table"] = "personnels"
                    result["email"] = email
                    return result
                else:
                    sql = """
                    select *
                    from students
                    where email = %s;
                    """  # SQL query to search the user by email
                    cursor.execute(sql, email)  # execute the query
                    result = cursor.fetchone()  # get the result
                    if result:
                        # add table name to the result
                        result["table"] = "students"
                        result["email"] = email
                        return result
                    else:
                        return None

    except pymysql.MySQLError:  # handle exceptions
        http_response(500, "An error occurred while searching the user credentials from database.")
