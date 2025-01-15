from flask import request
from flask_restx import Namespace, Resource, fields
from namespaces.tokenNamespace import get_token_info

import dao.userDao as userDao


dao = userDao.UserDAO()

ns = Namespace('users', description='User related operations')

user_model = ns.model('User', {
    'id': fields.Integer(readOnly=True, description='The user unique identifier'),
    'email': fields.String(required=True, description='The user email address'),
    'is_admin': fields.Boolean(required=True, description='Is the user an admin?'),
})

@ns.route('/')
class UserList(Resource):
    @ns.doc('list_users')
    @ns.marshal_list_with(user_model)
    def get(self):
        """List all users"""
        response = dao.get_all()
        if not response:
            ns.abort(404, "No users found")
        return response

@ns.route('/self')
class UserSelf(Resource):
    @ns.doc('get_user')
    @ns.marshal_with(user_model)
    def get(self):
        """Get the current user"""
        token = request.headers.get('Authorization')
        token_info = get_token_info(token)
        response = dao.get_by_id(token_info['user_id'])
        if not response:
            ns.abort(404, "User not found")
        return response
