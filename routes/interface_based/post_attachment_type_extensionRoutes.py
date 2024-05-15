from flask import (Blueprint, request)
from helpers.http_response import http_response
import helpers.jwt_token as jwt

bp = Blueprint('ib_post-attachment-type-extension', __name__)
