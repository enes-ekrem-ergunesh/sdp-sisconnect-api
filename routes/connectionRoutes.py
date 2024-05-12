from flask import (Blueprint, request)
from flask_bcrypt import Bcrypt
from helpers.http_response import http_response
import db.dbConnections as db
import helpers.jwt_token as jwt
import datetime
import pymysql

import db.connectionDao as connectionDao
import db.harmonyDao as harmonyDao

bp = Blueprint('connection', __name__)

TIMEZONE = datetime.timezone.utc


def time_ago(request_time):
    """
    Get time ago
    """
    request_time = request_time.replace(tzinfo=TIMEZONE)
    time_diff = datetime.datetime.now(TIMEZONE) - request_time
    if (time_diff.days // 365) > 0:
        if (time_diff.days // 365) == 1:
            return "a year ago"
        return f"{(time_diff.days // 365)} years ago"
    elif (time_diff.days // 30) > 0:
        if (time_diff.days // 30) == 1:
            return "a month ago"
        return f"{(time_diff.days // 30)} months ago"
    elif time_diff.days > 0:
        if time_diff.days == 1:
            return "a day ago"
        return f"{time_diff.days} days ago"
    elif time_diff.seconds > 3600:
        if time_diff.seconds // 3600 == 1:
            return "an hour ago"
        return f"{time_diff.seconds // 3600} hours ago"
    elif time_diff.seconds > 60:
        if time_diff.seconds // 60 == 1:
            return "a minute ago"
        return f"{time_diff.seconds // 60} minutes ago"
    else:
        if time_diff.seconds < 3:
            return "just now"
        return f"{time_diff.seconds} seconds ago"


@bp.route("/connection/hello", methods=["GET"])
def greet():
    """
    Greets the connection endpoint
    """
    return {
        "message": "Hello, connection!"
    }


@bp.route("/connection", methods=["GET"])
def get_all_connections():
    """
    Get all connections
    """
    connections = connectionDao.get_all_connections()
    return {
        "connections": connections
    }


@bp.route("/connection/user/<int:user_id>", methods=["GET"])
def get_connections_by_user_id(user_id):
    """
    Get all connections by user id
    """
    connections = connectionDao.get_connections_by_user_id(user_id)
    if connections:
        return connections
    else:
        return []


@bp.route("/connection/<int:connection_id>", methods=["GET"])
def get_connection_by_id(connection_id):
    """
    Get connection by id
    """
    connection = connectionDao.get_connection_by_id(connection_id)
    if connection:
        return connection
    else:
        return {}


@bp.route("/connection/between/<int:connected_user_id>", methods=["GET"])
def get_connection_between_users(connected_user_id):
    """
    Get connection between users
    """
    user_id = jwt.get_user(request)
    connection = connectionDao.get_connection_between_users(user_id, connected_user_id)
    if connection:
        return connection
    else:
        return {}


@bp.route("/connection/requests", methods=["GET"])
def get_connection_requests():
    """
    Get connection requests
    """
    user_id = jwt.get_user(request)
    connection_requests = connectionDao.get_connection_requests(user_id)
    # replace request time with time ago
    for r in connection_requests:
        r["time_ago"] = time_ago(r["request_time"])
        r.pop("request_time")
        _user_id = r["user_id"]
        harmonyDao.append_user_fields(r)
        fields = ["address", "birthdate", "created_at", "deleted_at", "email", "gender", "password", "student_id", "id",
                  "table", "updated_at", "personnel_id", "old_id", "phone_numbers", "school_email", "personal_email"]
        for field in fields:
            if field in r:
                r.pop(field)
        r["user_id"] = _user_id

    if connection_requests:
        return connection_requests
    else:
        return []


@bp.route("/connection", methods=["POST"])
def create_connection():
    """
    Create a connection
    """
    user_id = jwt.get_user(request)

    if "connected_user_id" not in request.json:
        http_response(400, "connected_user_id is required")
    connected_user_id = request.json.get("connected_user_id")

    existing_connection = connectionDao.get_connection_between_users(user_id, connected_user_id)
    if existing_connection:
        http_response(400, "Connection already exists")

    last_row = connectionDao.create_connection(user_id, connected_user_id)
    return {
        "message": "Connection created successfully",
    }


@bp.route("/connection", methods=["PUT"])
def update_connection():
    """
    Update a connection
    """
    user_id = jwt.get_user(request)

    if (
            "blocked" not in request.json
    ):
        http_response(400, "Invalid request")

    existing_connection = connectionDao.get_connection_by_id(request.json.get("id"))
    if not existing_connection:
        http_response(400, "Connection does not exist")
    elif existing_connection.get("user_id") != user_id:
        http_response(400, "Unauthorized")

    connectionDao.update_connection(request.json)
    return {
        "message": "Connection updated successfully"
    }


@bp.route("/connection/<int:connection_id>", methods=["DELETE"])
def delete_connection(connection_id):
    """
    Delete a connection
    """
    user_id = jwt.get_user(request)
    connectionDao.soft_delete_connection(user_id, connection_id)
    return {
        "message": "Connection deleted successfully"
    }


@bp.route("/connection/between/<int:connected_user_id>", methods=["DELETE"])
def delete_connection_between_users(connected_user_id):
    """
    Delete a connection between users
    """
    user_id = jwt.get_user(request)
    connection = connectionDao.get_connection_between_users(user_id, connected_user_id)
    if not connection:
        http_response(400, "Connection does not exist")

    connectionDao.soft_delete_connection_between_users(user_id, connected_user_id)
    return {
        "message": "Connection deleted successfully"
    }


@bp.route("/connection/accept/<int:connection_id>", methods=["PUT"])
def accept_connection(connection_id):
    """
    Accept a connection
    """
    user_id = jwt.get_user(request)

    connection = connectionDao.get_connection_by_id(connection_id)
    if not connection:
        http_response(400, "Connection does not exist")
    elif connection.get("connected_user_id") != user_id:
        http_response(401, "Unauthorized")
    elif connection.get("accepted_at"):
        http_response(400, "Connection already accepted")

    connectionDao.accept_connection(connection)
    return {
        "message": "Connection accepted successfully"
    }
