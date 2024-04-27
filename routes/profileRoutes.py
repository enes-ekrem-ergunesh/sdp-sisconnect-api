from flask import (Blueprint, request)
from helpers.http_response import http_response
import helpers.jwt_token as jwt

import db.profileDao as profileDao

bp = Blueprint('profile', __name__)


@bp.route("/profile", methods=["GET"])
def get_profile():
    """
    Gets the user profile
    """
    user_id = jwt.get_user(request)
    profile = profileDao.get_profile_id_by_user_id(user_id)
    if not profile:
        http_response(404, "Profile not found")
    return profile


@bp.route("/profile/about/fields/<int:profile_id>", methods=["GET"])
def get_profile_about_fields_by_profile_id(profile_id):
    """
    Retrieves profile about fields by profile id
    """
    profile_about_fields = profileDao.get_profile_about_fields_by_profile_id(profile_id)
    if not profile_about_fields:
        return []
    return profile_about_fields


@bp.route("/profile/about/fields/update", methods=["PUT"])
def update_profile_about_fields():
    """
    Updates the user profile about fields
    """
    user_id = jwt.get_user(request)
    profile_about_fields = request.json
    profileDao.update_profile_about_fields(profile_about_fields, user_id)
    return {
        "message": "Profile about fields updated"
    }
