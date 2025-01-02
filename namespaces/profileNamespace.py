from flask import request
from flask_restx import Namespace, Resource, fields
import dao.profileDao as profileDao

dao = profileDao.ProfileDAO()


ns = Namespace('profiles', description='Profile related operations')

profile_info_model = ns.model('Profile Info', {
    'id': fields.Integer(readOnly=True, description='The user unique identifier'),
    'user_id': fields.Integer(required=True, description='The user id'),
    'email': fields.String(required=True, description='The user email'),
    'first_name': fields.String(required=True, description='The user first name'),
    'last_name': fields.String(required=True, description='The user last name'),
    'is_admin': fields.Boolean(required=True, description='The user is admin'),
})

def get_profile_by_user_id(user_id):
    return dao.get_by_user_id(user_id)

@ns.route('/<int:user_id>')
class ProfileInfo(Resource):
    @ns.doc('get_profile')
    def get(self, user_id):
        """Get profile by user id"""
        profile_info = get_profile_by_user_id(user_id)
        return {"message": "getting profile"}
