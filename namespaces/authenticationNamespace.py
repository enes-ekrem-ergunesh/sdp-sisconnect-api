from flask_bcrypt import Bcrypt
from namespaces.tokenNamespace import *
from namespaces.profileNamespace import create_profile
from namespaces.profileFieldNamespace import insert_profile_field, generate_profile_field

import dao.userDao as userDao
import dao.studentDao as studentDao
import dao.personnelDao as personnelDao
import dao.harmonyStudentDao as harmonyStudentDao
import dao.harmonyPersonnelDao as harmonyPersonnelDao

bcrypt = Bcrypt()

user_dao = userDao.UserDAO()
token_dao = tokenDao.TokenDAO()
student_dao = studentDao.StudentDAO()
personnel_dao = personnelDao.PersonnelDAO()
harmony_student_dao = harmonyStudentDao.HarmonyStudentDAO()
harmony_personnel_dao = harmonyPersonnelDao.HarmonyPersonnelDAO()

ns = Namespace('authentication', description='Authentication related operations')

email_password_login_model = ns.model('EmailPasswordLogin', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password'),
    'remember_me': fields.Boolean(required=True, description='Remember me')
})

google_login_model = ns.model('GoogleLogin', {
    'id_token': fields.String(required=True, description='Google id token')
})


def is_existing_sis_account(email):
    if get_sis_user_by_email(email):
        return True
    return False


def get_sis_user_by_email(email):
    return user_dao.get_by_email(email)


def is_existing_harmony_account(email):
    if get_harmony_personnel_by_email(email) or get_harmony_student_by_email(email):
        return True
    return False


def get_harmony_personnel_by_email(email):
    return harmony_personnel_dao.get_by_email(email)


def get_harmony_student_by_email(email):
    return harmony_student_dao.get_by_email(email)


def get_harmony_by_email(email):
    if get_harmony_student_by_email(email):
        return get_harmony_student_by_email(email)
    elif get_harmony_personnel_by_email(email):
        return get_harmony_personnel_by_email(email)


def get_harmony_personnel_credentials(email):
    data = get_harmony_personnel_by_email(email)
    return {
        'harmony_personnel_id': data['id'],
        'email': data['school_email'],
        'password': data['password']
    }


def get_harmony_student_credentials(email):
    data = get_harmony_student_by_email(email)
    return {
        'harmony_student_id': data['id'],
        'email': data['email'],
        'password': data['password']
    }


def get_harmony_credentials(email):
    if get_harmony_student_by_email(email):
        return get_harmony_student_credentials(email)
    elif get_harmony_personnel_by_email(email):
        return get_harmony_personnel_credentials(email)


def create_sis_user(email):
    data = {
        'email': email,
    }
    return user_dao.create(data)


def create_sis_harmony_link_personnel(harmony_credentials):
    data = {
        'user_id': harmony_credentials['user_id'],
        'harmony_personnel_id': harmony_credentials['harmony_personnel_id']
    }
    personnel_dao.create(data)


def create_sis_harmony_link_student(harmony_credentials):
    data = {
        'user_id': harmony_credentials['user_id'],
        'harmony_student_id': harmony_credentials['harmony_student_id']
    }
    student_dao.create(data)


def is_student(email):
    if get_harmony_student_by_email(email):
        return True
    elif get_harmony_personnel_by_email(email):
        return False


def first_time_login(email):
    credentials = get_harmony_credentials(email)

    create_sis_user(email)

    credentials['user_id'] = get_sis_user_by_email(email)['id']

    profile_id = create_profile(credentials['user_id'])

    columns = get_harmony_by_email(email)
    import_profile_fields(profile_id, columns)

    if is_student(email):
        create_sis_harmony_link_student(credentials)
    else:
        create_sis_harmony_link_personnel(credentials)


def check_password(email, password):
    credentials = get_harmony_credentials(email)

    is_password_correct = bcrypt.check_password_hash(credentials['password'], password)
    if not is_password_correct:
        ns.abort(401, "Invalid email or password. Please try again.")


def import_profile_fields(profile_id, harmony_data):
    fields_to_import = {
        1: 'address',
        3: 'gender',
        4: 'birthdate',
    }
    for field_id, field_name in fields_to_import.items():
        if field_name in harmony_data:
            if harmony_data[field_name]:
                insert_profile_field(
                    generate_profile_field(
                        profile_id,
                        field_id,
                        harmony_data[field_name]
                    )
                )


@ns.route('/')
class EmailPasswordLogin(Resource):
    @ns.doc('login_with_email_password')
    @ns.expect(email_password_login_model)
    @ns.marshal_with(token_info_model)
    def post(self):
        """Login with email and password"""
        payload = ns.payload
        print('PAYLOAD', payload)

        # Check if email and password are provided
        if not payload['password'] or not payload['email'] or payload['email'] == '' or payload['password'] == '':
            ns.abort(400, "Email and password are required")

        if not is_existing_sis_account(payload['email']):
            if not is_existing_harmony_account(payload['email']):
                ns.abort(401, "Invalid email or password. Please try again.")
            else:
                first_time_login(payload['email'])

        check_password(payload['email'], payload['password'])

        token = generate_sis_token(payload['email'], payload['remember_me'])
        token_id = insert_token(get_sis_user_by_email(payload['email'])['id'], token)
        token_info = token_dao.get_by_id(token_id)

        return token_info


@ns.route('/google')
class GoogleLogin(Resource):
    @ns.doc('login_with_google')
    @ns.expect(google_login_model)
    @ns.marshal_with(token_info_model)
    def post(self):
        """Login with Google"""
        payload = ns.payload

        token = payload['id_token']
        email = decode_google_id_token(payload['id_token'])['email']

        if not is_existing_sis_account(email):
            if not is_existing_harmony_account(email):
                ns.abort(404, "Only SIS school Google accounts are allowed.")
            else:
                first_time_login(email)

        token_id = insert_token(get_sis_user_by_email(email)['id'], token, 'google')
        token_info = token_dao.get_by_id(token_id)

        return token_info
