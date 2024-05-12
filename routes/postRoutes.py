from flask import (Blueprint, request)
from helpers.http_response import http_response
import helpers.jwt_token as jwt
import datetime

import db.postDao as postDao

bp = Blueprint('post', __name__)

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


@bp.route("/post/hello", methods=["GET"])
def greet():
    """
    Greets the post endpoint
    """
    return {
        "message": "Hello, post!"
    }


@bp.route("/post", methods=["GET"])
def get_all_posts():
    """
    Get all posts
    """
    posts = postDao.get_all_posts()
    if posts:
        for post in posts:
            post["time_ago"] = time_ago(post.get("created_at"))
        return posts
    else:
        return []


@bp.route("/post/user/<int:user_id>", methods=["GET"])
def get_posts_by_user_id(user_id):
    """
    Get all posts by user id
    """
    posts = postDao.get_posts_by_user_id(user_id)
    if posts:
        for post in posts:
            post["time_ago"] = time_ago(post.get("created_at"))
        return posts
    else:
        return []


@bp.route("/post/<int:post_id>", methods=["GET"])
def get_post_by_id(post_id):
    """
    Get post by id
    """
    post = postDao.get_post_by_id(post_id)
    if post:
        post["time_ago"] = time_ago(post.get("created_at"))
        return post
    else:
        return {}


@bp.route("/post/connections", methods=["GET"])
def get_all_posts_of_connections():
    """
    Get all posts of connections
    """
    user_id = jwt.get_user(request)

    posts = postDao.get_all_posts_of_connections(user_id)

    if posts:
        for post in posts:
            post["time_ago"] = time_ago(post.get("created_at"))
        return posts
    else:
        return []


@bp.route("/post", methods=["POST"])
def create_post():
    """
    Create a post
    """
    user_id = jwt.get_user(request)

    if (
            "content" not in request.json
    ):
        http_response(400, "Invalid request")

    post_id = postDao.create_post(user_id, request.json)
    return {
        "message": "Post created successfully",
        "post_id": post_id
    }


@bp.route("/post/<int:post_id>", methods=["DELETE"])
def soft_delete_post(post_id):
    """
    Soft delete a post
    """
    user_id = jwt.get_user(request)

    post = postDao.get_post_by_id(post_id)
    if not post:
        http_response(400, "Post does not exist")
    elif post.get("user_id") != user_id:
        http_response(400, "Unauthorized")

    postDao.soft_delete_post(user_id, post_id)
    return {
        "message": "Post deleted successfully"
    }
