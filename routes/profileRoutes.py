from flask import (Blueprint, request)
from helpers.http_response import http_response
import helpers.jwt_token as jwt

import db.profileDao as profileDao

bp = Blueprint('profile', __name__)


@bp.route("/profile/about/<int:profile_id>", methods=["GET"])
def get_profile_about(profile_id):
    """
    Retrieves a profile about by id
    """
    user_id = jwt.decode_token(request.headers.get("Authorization").split(" ")[1])["user_id"]
    profile = profileDao.get_profile_about_by_id(profile_id, user_id)
    if not profile:
        http_response(404, "Not Found")
    return profile


@bp.route("/profile", methods=["GET"])
def get_profile():
    """
    Gets the user profile
    """
    user_id = jwt.decode_token(request.headers.get("Authorization").split(" ")[1])["user_id"]
    profile = profileDao.get_profile_id_by_user_id(user_id)
    if not profile:
        http_response(404, "Not Found")
    return profile
