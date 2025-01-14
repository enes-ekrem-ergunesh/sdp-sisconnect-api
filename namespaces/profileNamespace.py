from flask import request
from flask_restx import Namespace, Resource, fields
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
    _id = dao.get_by_user_id(user_id)['id']
    email = user_dao.get_by_id(user_id)['email']
    profile_info = {
        'id': _id,
        'user_id': user_id,
        'email': email,
        'first_name': get_personnel_by_email(email)['first_name'] if get_personnel_by_email(email) else get_student_by_email(email)['first_name'],

    }

    return profile_info



@ns.route('/<int:user_id>')
class ProfileInfo(Resource):
    @ns.doc('get_profile')
    def get(self, user_id):
        """Get profile by user id"""
        profile_info = collect_profile_info(user_id)
        return {"message": profile_info}
