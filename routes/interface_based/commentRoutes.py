from flask import (Blueprint, request)
from helpers.http_response import http_response
import helpers.jwt_token as jwt

import db.interface_based.commentDao as Dao

bp = Blueprint('ib_comment', __name__)


@bp.route("/ib_comment/hello", methods=["GET"])
def greet():
    return {
        "message": "Hello, ib_comment!"
    }


@bp.route("/ib_comment", methods=["GET"])
def get_all():
    dao = Dao.CommentDao()
    result = dao.get_all()
    if result:
        return result
    else:
        return []
