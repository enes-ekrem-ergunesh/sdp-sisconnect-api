from flask import request
from flask_restx import Namespace, Resource, fields
from namespaces.tokenNamespace import get_token_info
from namespaces.profileNamespace import collect_profile_info, profile_info_model

import dao.userDao as userDao


dao = userDao.UserDAO()

ns = Namespace('users', description='User related operations')

user_model = ns.model('User', {
    'id': fields.Integer(readOnly=True, description='The user unique identifier'),
    'email': fields.String(required=True, description='The user email address'),
    'is_admin': fields.Boolean(required=True, description='Is the user an admin?'),
})

def search_users(search_term):
    search_term = str.lower(search_term)
    sis_users = dao.get_all()
    search_results = []
    for user in sis_users:
        profile_info = collect_profile_info(user['id'])
        if (search_term in str.lower(profile_info['first_name'])
                or search_term in str.lower(profile_info['last_name']))\
                or search_term in str.lower(user['email']):
            search_results.append(profile_info)
    return search_results


@ns.route('/<string:search_term>')
class UserSearch(Resource):
    @ns.doc('search_users')
    @ns.marshal_list_with(profile_info_model)
    def get(self, search_term):
        """Search for users by name or email"""
        return search_users(search_term)


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
