from flask import abort
from flask_restx import Namespace, Resource, fields
import dao.profileFieldDao as profileDao
import dao.profileFieldTypeDao as profileFieldTypeDao

dao = profileDao.ProfileFieldDAO()
profile_field_type_dao = profileFieldTypeDao.ProfileFieldTypeDAO()


ns = Namespace('profileFields', description='Profile Field related operations')

profile_field_model = ns.model('ProfileField', {
    'id': fields.Integer(readOnly=True, description='The profile field identifier'),
    'profile_id': fields.Integer(required=True, description='The profile identifier'),
    'profile_field_type_id': fields.Integer(required=True, description='The profile field type identifier'),
    'profile_field_type': fields.String(required=True, description='The profile field type'),
    'profile_field_data_type': fields.String(required=True, description='The profile field data type'),
    'value': fields.String(required=True, description='The value of the profile field')
})

profile_field_create_model = ns.model('ProfileFieldCreate', {
    'profile_id': fields.Integer(required=True, description='The profile identifier'),
    'profile_field_type_id': fields.Integer(required=True, description='The profile field type identifier'),
    'value': fields.String(required=True, description='The value of the profile field')
})

def get_profile_field(profile_field_id):
    profile_field = dao.get_by_id(profile_field_id)
    if profile_field is None:
        abort(404, "Profile field does not exist")
    profile_field_type = profile_field_type_dao.get_by_id(profile_field['profile_field_type_id'])
    profile_field['profile_field_type'] = profile_field_type['name']
    profile_field['profile_field_data_type'] = profile_field_type['data_type']
    return profile_field

def insert_profile_field(profile_field):
    print(f"PROFILE FIELD INSERTING: {profile_field}")
    return dao.create(profile_field)

def generate_profile_field(profile_id, profile_field_type_id, value):
    return {
        'profile_id': profile_id,
        'profile_field_type_id': profile_field_type_id,
        'value': value
    }

@ns.route('/<int:profile_field_id>')
class ProfileFieldById(Resource):
    @ns.doc('get_profile_field')
    @ns.marshal_with(profile_field_model)
    def get(self, profile_field_id):
        """Get profile field by id"""
        profile_field = get_profile_field(profile_field_id)
        if profile_field is None:
            abort(404, "Profile field does not exist")
        return profile_field

@ns.route('/')
class ProfileField(Resource):
    @ns.doc('create_profile_field')
    @ns.expect(profile_field_create_model)
    def post(self):
        """Create a new profile field"""
        try:
            insert_profile_field(ns.payload)
            return {
                'message': 'Profile field created successfully'
            }
        except Exception as e:
            abort(400, str(e))
