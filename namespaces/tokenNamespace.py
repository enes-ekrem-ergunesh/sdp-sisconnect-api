from flask import request
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

def validate_token(token):
    token_info = dao.get_by_token(token)
    if not token_info:
        ns.abort(401, "Invalid token")
        return None
    if UTC.localize(token_info['valid_until']) < datetime.now(UTC):
        ns.abort(401, "Token expired")
        return None
    if token_info['revoked_at']:
        ns.abort(401, "Token revoked")
        return None
    return token_info['user_id']

def revoke_token(token):
    token_info = dao.get_by_token(token)
    dao.update(token_info['id'], {'revoked_at': datetime.now(UTC)})

@ns.route('/')
class TokenInfo(Resource):
    @ns.doc('verify_token')
    def get(self):
        """Verify token (using middleware in wsgi file)"""
        return {"message": "Token is valid"}

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

    @ns.doc('revoke_token')
    def put(self):
        """Revoke token"""
        _token = request.headers.get('Authorization')
        revoke_token(_token)
        return {"message": "Token revoked successfully"}
