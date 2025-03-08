from flask import Flask, request, abort
from flask_cors import CORS
from flask_restx import Api, apidoc
from werkzeug.middleware.proxy_fix import ProxyFix
import logging

from constants import *
from namespaces.userNamespace import ns as user_namespace
from namespaces.harmonyPersonnelNamespace import ns as harmony_personnel_namespace
from namespaces.harmonyStudentNamespace import ns as harmony_student_namespace
from namespaces.tokenNamespace import ns as token_namespace
from namespaces.authenticationNamespace import ns as authentication_namespace
from namespaces.profileNamespace import ns as profile_namespace
from namespaces.profileFieldNamespace import ns as profile_field_namespace
from namespaces.connectionNamespace import ns as connections_namespace
from namespaces.postNamespace import ns as post_namespace
from namespaces.postLikeNamespace import ns as post_like_namespace

from namespaces.tokenNamespace import validate_token

logging.basicConfig(
    filename='app.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.config['ERROR_404_HELP'] = False # Disable error help messages from flask-restx (uncomment on production)

if PROD:
    app.wsgi_app = ProxyFix(
        app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
    )

CORS(app)

api = Api(
    app,
    version='1.0',
    title='SIS Connect API',
    description='A simple API',
    authorizations=AUTHORIZATIONS,
    security='JWT Token',
)

api.add_namespace(user_namespace)
api.add_namespace(harmony_personnel_namespace)
api.add_namespace(harmony_student_namespace)
api.add_namespace(token_namespace)
api.add_namespace(authentication_namespace)
api.add_namespace(profile_namespace)
api.add_namespace(profile_field_namespace)
api.add_namespace(connections_namespace)
api.add_namespace(post_namespace)
api.add_namespace(post_like_namespace)

@api.documentation
def custom_ui():
    return apidoc.ui_for(api) + """
    <style>
        @media (prefers-color-scheme: dark) {
            html {
                filter: invert(1);
            }
            .backdrop-ux {
                background: rgba(220,220,220,.9) !important;
            }
            .modal-ux {
                box-shadow: 0 10px 30px 0 rgb(0 0 0 / 5%) !important;
            }
            .microlight {
                filter: invert(1);
        }
    </style>
    """

@app.before_request
def before_request():
    # Allow all options requests (pre-flight requests for CORS)
    if request.method == "OPTIONS":
        return

    if request.endpoint in ALLOWED_ENDPOINTS:
        return

    print("NOT ALLOWED ENDPOINT:", request.endpoint)
    # print("NOT ALLOWED request:", request)

    _token = request.headers.get('Authorization')
    if not _token:
        abort(401, 'Token is missing')

    user_id = validate_token(_token)

    request.user_id = user_id

if __name__ == '__main__':
    app.run(debug=True)