from flask import (Blueprint, request)
from flask_bcrypt import Bcrypt
from helpers.http_response import http_response
import db.dbConnections as db
import helpers.jwt_token as jwt
import datetime
import pymysql

bp = Blueprint('user', __name__)
bcrypt = Bcrypt()

TIMEZONE = datetime.timezone.utc


def db_get_user_by_email_sc(email):
    """
    Get a user by email

    Args:
    email (str): the email of the user

    Returns:
    dict: user data
    """

    # get a connection to the database (sisConnect)
    connection = db.get_connection()
    try:  # try to get the user by email
        with connection:  # use the connection
            with connection.cursor() as cursor:  # get a cursor
                # get user as personnel
                sql = """
                select *
                from users u
                join personnels p on u.id = p.user_id
                where u.email = %s;
                """  # SQL query to get the user by email
                cursor.execute(sql, email)  # execute the query
                result = cursor.fetchone()  # get the result
                if result:  # if the result is not None, return the result
                    return result
                else:  # if the result is None, get user as student
                    sql = """
                    select *
                    from users u
                    join students s on u.id = s.user_id
                    where u.email = %s;
                    """  # SQL query to get the user by email
                    cursor.execute(sql, email)  # execute the query
                    result = cursor.fetchone()  # get the result
                    return result
    except pymysql.MySQLError:  # handle exceptions
        http_response(500, "An error occurred while getting the user credentials from database.")


def db_get_user_by_email_h(email):
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


def db_insert_user_sc(user):
    """
    Inserts a user into the database

    Args:
    user: dict
    """
    # Insert the user into the user table in the sisConnect database
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

    # Insert the user into the personnel or student table in the sisConnect database
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


def db_insert_token(token, user_id, valid_until):
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


@bp.route("/user/hello", methods=["GET"])
def greet():
    """
    Greets the user endpoint
    """
    return {
        "status": 200,
        "message": "Hello, user!"
    }


@bp.route("/user/login", methods=["POST"])
def login():
    """
    Logs in a user

    Prerequisites:
    Headers: Content-Type: application/json
    Body: {"email": <email>, "password": <password>, "remember_me": true/false}

    Returns:
    str: token
    """

    # check if the request is valid
    if (
            not request.json
            or "email" not in request.json
            or "password" not in request.json
            or "remember_me" not in request.json
    ):
        http_response(400, "Invalid request.")

    # get the user by email from sisConnect database
    user = db_get_user_by_email_sc(request.json["email"])

    # check if the user exists in sisConnect database
    if user:
        user_h = db_get_user_by_email_h(request.json["email"])
        # append all the fields from user_h to user if not already present
        for key in user_h:
            if key not in user:
                user[key] = user_h[key]
        # remove unnecessary user_id field
        user.pop("user_id")

    # if the user does not exist in the sisConnect database
    else:
        # get the user by email from harmony database
        user = db_get_user_by_email_h(request.json["email"])

        # check if the user exists in harmony database
        if not user:
            http_response(400, "Invalid email or password.")

        # check if the password is correct
        if not bcrypt.check_password_hash(user["password"], request.json["password"]):
            http_response(400, "Invalid email or password.")

        # add the user to the sisConnect database
        db_insert_user_sc(user)

        user_sc = db_get_user_by_email_sc(request.json["email"])
        # append all the fields from user_sc to user
        for key in user_sc:
            user[key] = user_sc[key]
        # remove unnecessary user_id field
        user.pop("user_id")

    # check if the password is correct
    if not bcrypt.check_password_hash(user["password"], request.json["password"]):
        http_response(400, "Invalid email or password.")

    # generate a token
    created_at = datetime.datetime.now(tz=TIMEZONE)  # get the current time
    valid_until = (
        datetime.datetime.now(tz=TIMEZONE) + datetime.timedelta(days=7)
        if request.json["remember_me"]
        else datetime.datetime.now(tz=TIMEZONE) + datetime.timedelta(hours=1)
    )  # set the token validity
    token = jwt.create_token(
        {
            "user_id": user["id"],
            "email": user["email"],
            "created_at": created_at.isoformat(),
            "valid_until": valid_until.isoformat(),
        }
    )

    # add the token to the db
    db_insert_token(token, user["id"], valid_until.isoformat())

    return {
        "token": token
    }
