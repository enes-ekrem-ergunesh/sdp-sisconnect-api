from flask import Flask, request
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from helpers.jwt_token import decode_token, verify_token
from helpers.http_response import http_response
from importlib import import_module

import routes.userRoutes
import routes.profileRoutes
import routes.connectionRoutes
import routes.postRoutes

app = Flask(__name__)
CORS(app)  # Apply CORS for all routes
bcrypt = Bcrypt(app)

app.register_blueprint(routes.userRoutes.bp)
app.register_blueprint(routes.profileRoutes.bp)
app.register_blueprint(routes.connectionRoutes.bp)
app.register_blueprint(routes.postRoutes.bp)

# Interface-based imports and routes
basePath = "routes.interface_based"

for blueprint_name in ["commentRoutes",
                       "groupRoutes",
                       "notificationRoutes",
                       "post_attachment_type_extensionRoutes",
                       "post_interactionRoutes",
                       "profile_fieldRoutes",
                       "tokenRoutes",
                       "userRoutes",
                       "connectionRoutes",
                       "messageRoutes",
                       "post_attachmentRoutes",
                       "post_attachment_typeRoutes",
                       "postRoutes",
                       "profileRoutes",
                       "user_groupRoutes"
                       ]:
    # Import the blueprint module
    blueprint_module = import_module(f"{basePath}.{blueprint_name}")
    # Register the blueprint from the imported module
    app.register_blueprint(blueprint_module.bp)


@app.route("/")
def hello_world():
    return {"message": "Hello, World!"}


@app.before_request
def check_authorization():
    no_auth_routes = [
        "/", "/user/hello", "/user/login",
        "/ib_comment/hello"
    ]
    if request.path in no_auth_routes:
        return

    # bypass if request is an OPTIONS
    if request.method == "OPTIONS":
        return

    # check if the token is present
    if not request.headers.get("Authorization"):
        http_response(401, "Unauthorized!")

    # get the token and user id
    _token = request.headers.get("Authorization").split(" ")[1]
    _user_id = decode_token(_token)["user_id"]

    # verify the token
    if not verify_token(_token, _user_id):
        http_response(401, "Unauthorized!")
