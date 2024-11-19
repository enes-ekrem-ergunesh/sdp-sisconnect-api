from flask_restx import Namespace, Resource, fields
import dao.tokenDao as tokenDao

import jwt
import pytz
from config import config
from datetime import datetime, timedelta

from google.oauth2 import id_token
from google.auth.transport import requests

import hashlib
from pymysql.err import IntegrityError

dao = tokenDao.TokenDAO()
UTC = pytz.utc


ns = Namespace('tokens', description='Token related operations')

token_info_model = ns.model('Token Info', {
    'id': fields.Integer(readOnly=True, description='The user unique identifier'),
    'user_id': fields.Integer(required=True, description='The user id'),
    'token_type_id': fields.Integer(required=True, description='The token type id'),
    'token': fields.String(required=True, description='The token'),
    'valid_until': fields.DateTime(required=True, description='The token expiration date'),
    'revoked_at': fields.DateTime(description='The token revocation date'),
})

token_model = ns.model('Token', {
    'token': fields.String(required=True, description='The token'),
})


def decode_google_id_token(token):
    try:
        return id_token.verify_oauth2_token(token, requests.Request(), config.get('GOOGLE_WEB_CLIENT_ID'))
    except ValueError:
        ns.abort(400, "Invalid Google token")
        return None

def generate_sis_token(email, remember_me=False):
    key = config.get('JWT_SECRET')
    session_duration = timedelta(weeks=1) if remember_me else timedelta(hours=1)

    payload = {
        "email": email,
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + session_duration
    }
    return jwt.encode(payload, key, algorithm='HS256')

def insert_token(user_id, token, token_type='sis'):
    if token_type == 'sis':
        token_type_id = 1
        exp = jwt.decode(token, config.get('JWT_SECRET'), algorithms='HS256')['exp']
    elif token_type == 'google':
        token_type_id = 2
        exp = decode_google_id_token(token)['exp']
    else:
        ns.abort(400, "Invalid token type")
        return None

    data = {
        'user_id': user_id,
        'token_type_id': token_type_id,
        'token': token,
        'token_hash': hashlib.sha256(token.encode('utf-8')).hexdigest(),
        'valid_until': datetime.fromtimestamp(exp, UTC)
    }
    try:
        return dao.create(data)
    except IntegrityError:
        ns.abort(400, "Token already exists")
        return None


@ns.route('/')
class TokenInfo(Resource):
    @ns.doc('get_token_info')
    @ns.expect(token_model)
    @ns.marshal_with(token_info_model)
    def post(self):
        """Get token info"""
        data = ns.payload
        print(data)
        response = dao.get_by_token(data['token'])
        if not response:
            ns.abort(404, "Token not found")
        return response