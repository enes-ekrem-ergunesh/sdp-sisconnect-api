from flask_restx import Namespace, Resource, fields
import dao.harmonyStudentDao as harmonyStudentDao

dao = harmonyStudentDao.HarmonyStudentDAO()

ns = Namespace('harmonyStudents', description='Harmony student related operations')

h_student = ns.model('HarmonyStudent', {
    'id': fields.Integer(readOnly=True, description='The student identifier'),
    'student_id': fields.String(required=True, description='The student ID'),
    'first_name': fields.String(required=True, description='The student first name'),
    'family_name': fields.String(required=True, description='The student family name'),
    'gender': fields.String(required=True, description='Gender of the student'),
    'birthdate': fields.Date(required=True, description='Birthdate of the student'),
    'address': fields.String(required=True, description='Address of the student'),
    'password': fields.String(required=True, description='Password of the student'),
    'email': fields.String(required=True, description='Email of the student'),
})

h_student_login = ns.model('HarmonyStudentLogin', {
    'email': fields.String(required=True, description='The email of the student'),
    'password': fields.String(required=True, description='The password of the student'),
})


@ns.route('/')
class HarmonyStudentList(Resource):
    @ns.doc('list_harmony_students')
    @ns.marshal_list_with(h_student)
    def get(self):
        """List all harmony students"""
        response = dao.get_all()
        if not response:
            ns.abort(404, "No harmony students found")
        return response

def get_student_by_email(email):
    response = dao.get_by_email(email)
    if not response:
        return None
    return response

@ns.route('/<string:email>')
class HarmonyStudentByEmail(Resource):
    @ns.doc('get_student_by_email')
    @ns.marshal_with(h_student)
    def get(self, email):
        """Get student by email"""
        response = get_student_by_email(email)
        if not response:
            ns.abort(404, "Student not found")
        return response
