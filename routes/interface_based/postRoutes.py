from flask import (Blueprint, request)
from helpers.http_response import http_response
import helpers.jwt_token as jwt

import db.interface_based.postDao as Dao

ROUTE = 'ib_post'
bp = Blueprint(ROUTE, __name__)

ADMIN = True
OWNER_COL = "user_id"


def validate_request(data, required):
    for field in required:
        if field not in data:
            http_response(400, f"Field '{field}' is required")


@bp.route(f"/{ROUTE}/hello", methods=["GET"])
def greet():
    return {
        "message": f"Hello, {ROUTE}!"
    }


def _get_all(_request, filters, admin=False):
    dao = Dao.PostDao()
    admin_id = jwt.get_user(_request) if admin else None
    result = dao.get_all(filters, admin, admin_id)
    if result:
        return result
    else:
        return []


@bp.route(f"/{ROUTE}", methods=["GET"])
def get_all():
    return _get_all(request, None)


@bp.route(f"/{ROUTE}/own", methods=["GET"])
def get_all_own():
    filters = {f"{OWNER_COL} = %s": jwt.get_user(request)}
    return _get_all(request, filters)


@bp.route(f"/{ROUTE}/user/<int:user_id>", methods=["GET"])
def get_all_by_user_id(user_id):
    filters = {f"{OWNER_COL} = %s": user_id}
    return _get_all(request, filters)


def _get(_id, _request, filters, admin=False):
    dao = Dao.PostDao()
    admin_id = jwt.get_user(_request) if admin else None
    result = dao.get_by_id(_id, filters, admin, admin_id)
    if result:
        return result
    else:
        return []


@bp.route(f"/{ROUTE}/<int:_id>", methods=["GET"])
def get(_id):
    return _get(_id, request, None)


@bp.route(f"/{ROUTE}/own/<int:_id>", methods=["GET"])
def get_own(_id):
    filters = {f"{OWNER_COL} = %s": jwt.get_user(request)}
    return _get(_id, request, filters)


@bp.route(f"/{ROUTE}", methods=["POST"])
def insert():
    data = request.get_json()
    dao = Dao.PostDao()
    user_id = jwt.get_user(request)
    required = ["content", "visibility_id"]

    validate_request(data, required)
    data["user_id"] = user_id
    result = dao.insert(data)
    return {
        "message": f"Inserted successfully with id: {result}"
    }


def _update(_id, _request, filters, admin=False):
    data = request.get_json()
    dao = Dao.PostDao()
    required = ["content", "visibility_id"]
    admin_id = jwt.get_user(_request) if admin else None

    validate_request(data, required)
    dao.update(data, _id, filters, admin, admin_id)
    return {
        "message": "Updated successfully"
    }


@bp.route(f"/{ROUTE}/<int:_id>", methods=["PUT"])
def update(_id):
    return _update(_id, request, None, ADMIN)


@bp.route(f"/{ROUTE}/own/<int:_id>", methods=["PUT"])
def update_own(_id):
    filters = {f"{OWNER_COL} = %s": jwt.get_user(request)}
    return _update(_id, request, filters)


def _delete(_request, filters, admin=False):
    dao = Dao.PostDao()
    admin_id = jwt.get_user(_request) if admin else None
    dao.delete(filters, admin, admin_id)
    return {
        "message": "Deleted successfully"
    }


@bp.route(f"/{ROUTE}/<int:_id>", methods=["DELETE"])
def delete(_id):
    filters = {f"id = %s": _id}
    return _delete(request, filters, ADMIN)


@bp.route(f"/{ROUTE}/user/<int:user_id>", methods=["DELETE"])
def delete_all_by_user_id(user_id):
    filters = {f"{OWNER_COL} = %s": user_id}
    return _delete(request, filters, ADMIN)


def _soft_delete(_request, filters, admin=False):
    dao = Dao.PostDao()
    admin_id = jwt.get_user(_request) if admin else None
    dao.soft_delete(filters, admin, admin_id)
    return {
        "message": "Deleted successfully"
    }


@bp.route(f"/{ROUTE}/soft/<int:_id>", methods=["DELETE"])
def soft_delete(_id):
    filters = {f"id = %s": _id}
    return _soft_delete(request, filters, ADMIN)


@bp.route(f"/{ROUTE}/soft/own/<int:_id>", methods=["DELETE"])
def soft_delete_own(_id):
    filters = {
        f"{OWNER_COL} = %s": jwt.get_user(request),
        "id = %s": _id
    }
    return _soft_delete(request, filters)


@bp.route(f"/{ROUTE}/soft/user/<int:user_id>", methods=["DELETE"])
def soft_delete_all_by_user_id(user_id):
    filters = {f"{OWNER_COL} = %s": user_id}
    return _soft_delete(request, filters, ADMIN)
