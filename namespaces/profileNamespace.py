from flask import abort, request
from flask_restx import Namespace, Resource, fields
from namespaces.tokenNamespace import get_token_info

import dao.profileDao as profileDao
import dao.userDao as userDao
from namespaces.harmonyStudentNamespace import get_student_by_email
from namespaces.harmonyPersonnelNamespace import get_personnel_by_email

dao = profileDao.ProfileDAO()
user_dao = userDao.UserDAO()


ns = Namespace('profiles', description='Profile related operations')

profile_info_model = ns.model('Profile Info', {
    'id': fields.Integer(readOnly=True, description='The user unique identifier'),
    'user_id': fields.Integer(required=True, description='The user id'),
    'email': fields.String(required=True, description='The user email'),
    'first_name': fields.String(required=True, description='The user first name'),
    'last_name': fields.String(required=True, description='The user last name'),
    'is_admin': fields.Boolean(required=True, description='The user is admin'),
})

def collect_profile_info(user_id):
    if not dao.get_by_user_id(user_id):
        return None
    _id = dao.get_by_user_id(user_id)['id']
    user = user_dao.get_by_id(user_id)
    email = user['email']
    if get_personnel_by_email(email):
        harmony_data = get_personnel_by_email(email)
    else:
        harmony_data = get_student_by_email(email)
    profile_info = {
        'id': _id,
        'user_id': user_id,
        'email': email,
        'first_name': harmony_data['first_name'],
        'last_name': harmony_data['family_name'],
        'is_admin': user['is_admin']
    }

    return profile_info

def create_profile(user_id):
    return dao.create({
        'user_id': user_id
    })

@ns.route('/<int:user_id>')
class ProfileInfo(Resource):
    @ns.doc('get_profile')
    def get(self, user_id):
        """Get profile by user id"""
        profile_info = collect_profile_info(user_id)
        if not profile_info:
            abort(404, "Profile not found")
        return profile_info

@ns.route('/')
class OwnProfileInfo(Resource):
    @ns.doc('get_own_profile')
    def get(self):
        """Get own profile"""
        token = request.headers.get('Authorization')
        token_info = get_token_info(token)
        profile_info = collect_profile_info(token_info['user_id'])
        if not profile_info:
            abort(404, "Profile not found")
        return profile_info