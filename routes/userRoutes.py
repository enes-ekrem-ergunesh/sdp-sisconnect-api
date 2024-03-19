from flask import (Blueprint, request)

bp = Blueprint('user', __name__)

bp.route("/login", methods=['POST'])
