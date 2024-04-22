from flask import (Blueprint, request)
from flask_bcrypt import Bcrypt
from helpers.http_response import http_response
import db.dbConnections as db
import helpers.jwt_token as jwt
import datetime
import pymysql

import db.userDao as userDao
import db.harmonyDao as harmonyDao

bp = Blueprint('user', __name__)
bcrypt = Bcrypt()

TIMEZONE = datetime.timezone.utc


def generate_token(user):
    """
    Generates a token for the user and inserts it into the database

    Args:
        user: dict

    Returns:
        token: str
    """
    created_at = datetime.datetime.now(tz=TIMEZONE)  # get the current time
    valid_until = (
        datetime.datetime.now(tz=TIMEZONE) + datetime.timedelta(days=7)
        if request.json["rememberMe"]
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
    userDao.insert_token(token, user["id"], valid_until.isoformat())
    return token


def first_time_login(email, password):
    """
    Checks if the user exists in the harmony database and if the password is correct

    Args:
    email: str
    password: str
    """
    # get the user by email from harmony database
    user = harmonyDao.get_user_by_email(email)

    # check if the user exists in harmony database
    if not user:
        http_response(400, "Invalid email or password.")

    # check if the password is correct
    if not bcrypt.check_password_hash(user["password"], password):
        http_response(400, "Invalid email or password.")

    return user


@bp.route("/user/hello", methods=["GET"])
def greet():
    """
    Greets the user endpoint
    """
    return {
        "message": "Hello, user!"
    }


@bp.route("/user/verify", methods=["GET"])
def verify():
    """
    Verifies the user

    Prerequisites:
    Headers: Authorization: Bearer <token>

    Returns:
    dict: user_id
    """

    token = request.headers.get("Authorization").split(" ")[1]
    user_id = jwt.decode_token(token)["user_id"]
    return {
        "user_id": user_id
    }


@bp.route("/user/login", methods=["POST"])
def login():
    """
    Logs in a user

    Prerequisites:
    Headers: Content-Type: application/json
    Body: {"email": <email>, "password": <password>, "rememberMe": true/false}

    Returns:
    str: token
    """

    # check if the request is valid
    if (
            not request.json
            or "email" not in request.json
            or "password" not in request.json
            or "rememberMe" not in request.json
    ):
        http_response(400, "Invalid request.")

    user = userDao.get_user_by_email(request.json["email"])  # get the user by email from sisConnect database

    if user:  # if user exists in the sisConnect database
        harmonyDao.append_user_fields(user)  # get the user details from the harmony database

    else:  # if the user does not exist in the sisConnect database
        user = first_time_login(request.json["email"], request.json["password"])  # login for the first time

        userDao.insert_user(user)  # insert the user to the sisConnect database

        userDao.append_user_fields(user, request.json["email"])  # get the user details from the sisConnect database

    # check if the password is correct
    if not bcrypt.check_password_hash(user["password"], request.json["password"]):
        http_response(400, "Invalid email or password.")

    # generate a token
    token = generate_token(user)

    return {
        "token": token
    }


@bp.route("/user/logout", methods=["POST"])
def logout():
    """
    Logs out a user

    Prerequisites:
    Headers: Authorization: Bearer <token>

    Returns:
    str: message
    """

    token = request.headers.get("Authorization").split(" ")[1]  # get the token
    user_id = jwt.decode_token(token)["user_id"]  # get the user id

    return userDao.revoke_token(token, user_id)  # revoke the token


@bp.route("/user", methods=["GET"])
def get_user():
    """
    Gets the user
    """

    _user_id = jwt.decode_token(request.headers.get("Authorization").split(" ")[1])["user_id"]
    user = userDao.get_user_by_id(_user_id)

    harmonyDao.append_user_fields(user)

    sensitive_fields = [
        "password", "created_at", "deleted_at", "updated_at", "student_id"
    ]

    for field in sensitive_fields:
        if field in user:
            user.pop(field)

    return user


@bp.route("/user/profile", methods=["GET"])
def profile():
    """
    Gets the user profile

    Prerequisites:
    Headers: Authorization: Bearer

    Returns:
    dict: user profile
    """

    token = request.headers.get("Authorization").split(" ")[1]  # get the token
    user_id = jwt.decode_token(token)["user_id"]  # get the user id from the token
    user = userDao.get_user_by_id_sc(user_id)  # get the user by id from the sisConnect database
    harmonyDao.append_user_fields(user)  # get the user details from the harmony database
    user.pop("password")  # remove the password from the user

    return {
        "user": user
    }
