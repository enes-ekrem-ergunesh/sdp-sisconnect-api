from flask_restx import Namespace, Resource, fields
import dao.harmonyPersonnelDao as harmonyPersonnelDao

dao = harmonyPersonnelDao.HarmonyPersonnelDAO()

ns = Namespace('harmonyPersonnels', description='Harmony personnel related operations')

h_personnel = ns.model('HarmonyPersonnel', {
    'id': fields.Integer(readOnly=True, description='The harmony personnel unique identifier'),
    'personnel_id': fields.String(required=True, description='The personnel id'),
    'first_name': fields.String(required=True, description='The first name of the personnel'),
    'family_name': fields.String(required=True, description='The family name of the personnel'),
    'personal_email': fields.String(required=True, description='The personal email address of the personnel'),
    'school_email': fields.String(required=True, description='The school email address of the personnel'),
    'password': fields.String(required=True, description='The password of the personnel'),
    'phone_numbers': fields.String(required=True, description='The phone numbers of the personnel'),
    'gender': fields.String(required=True, description='The gender of the personnel'),
    'birthdate': fields.Date(required=True, description='The birthdate of the personnel'),
    'old_id': fields.String(required=True, description='The old id of the personnel'),
})

h_personnel_login = ns.model('HarmonyPersonnelLogin', {
    'school_email': fields.String(required=True, description='The school email address of the personnel'),
    'password': fields.String(required=True, description='The password of the personnel'),
})


@ns.route('/')
class HarmonyPersonnelList(Resource):
    @ns.doc('list_harmony_personnels')
    @ns.marshal_list_with(h_personnel)
    def get(self):
        """List all harmony personnels"""
        response = dao.get_all()
        if not response:
            ns.abort(404, "No harmony personnels found")
        return response