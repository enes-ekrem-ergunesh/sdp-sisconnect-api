from flask import (Blueprint, request)
from helpers.http_response import http_response
import helpers.jwt_token as jwt

import db.profileDao as profileDao
import db.userDao as userDao
import db.harmonyDao as harmonyDao

bp = Blueprint('profile', __name__)


def validate_username(username):
    """
    Validates the username
    """
    if not username:
        http_response(400, "Invalid profile username")
    username_fields = username.split("_")
    name, user_id = username_fields[0], username_fields[1]
    if not name:
        http_response(400, "Invalid profile username")
    if not user_id:
        http_response(400, "Invalid profile username")
    # if user_id is not a number
    if not user_id.isdigit():
        http_response(400, "Invalid profile username")

    user = userDao.get_user_by_id(user_id)
    if not user:
        http_response(404, "Invalid profile username")

    user_h = harmonyDao.get_user_by_email(user["email"])
    if not user_h:
        http_response(404, "Invalid profile username")

    first_name = user_h["first_name"].replace(" ", "").lower()
    family_name = user_h["family_name"].replace(" ", "").lower()

    if name != (first_name + family_name):
        http_response(404, "Invalid profile username")

    return user_id


@bp.route("/profile/<string:username>", methods=["GET"])
def get_profile(username):
    """
    Gets the user profile
    """
    user_id = validate_username(username)
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
    for field in profile_about_fields:
        if not field["data"]:
            http_response(400, "Value is required")
    profileDao.update_profile_about_fields(profile_about_fields, user_id)
    return {
        "message": "Profile about fields updated"
    }


@bp.route("/profile/about/fields/types", methods=["GET"])
def get_profile_about_fields_types():
    """
    Retrieves profile about fields types
    """
    profile_about_fields_types = profileDao.get_profile_field_types()
    return profile_about_fields_types


@bp.route("/profile/about/fields/types/empty/<int:profile_id>", methods=["GET"])
def get_empty_profile_about_fields_types(profile_id):
    """
    Retrieves profile about fields types that are not in the profile
    """
    profile_about_fields_types = profileDao.get_profile_field_types()
    empty_profile_about_fields_types = profileDao.get_empty_profile_field_types_by_profile_id(profile_id)
    for field in profile_about_fields_types:
        if field in empty_profile_about_fields_types:
            field["empty"] = True
        else:
            field["empty"] = False

    return profile_about_fields_types
