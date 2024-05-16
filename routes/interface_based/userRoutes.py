from flask import (Blueprint, request)
from helpers.http_response import http_response
import helpers.jwt_token as jwt

import db.interface_based.userDao as Dao

bp = Blueprint('ib_user', __name__)


@bp.route("/ib_user/hello", methods=["GET"])
def greet():
    return {
        "message": "Hello, ib_user!"
    }


@bp.route("/ib_user", methods=["GET"])
def get_all():
    dao = Dao.UserDao()
    result = dao.get_all()
    if result:
        return result
    else:
        return []
