from flask import Flask, request
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from helpers.jwt_token import decode_token, verify_token
from helpers.http_response import http_response
import db.dbConnections as sCDB
import routes.userRoutes

app = Flask(__name__)
CORS(app)  # Apply CORS for all routes
bcrypt = Bcrypt(app)

app.register_blueprint(routes.userRoutes.bp)


@app.route("/")
def hello_world():
    connection = sCDB.get_connection()
    with connection:
        with connection.cursor() as cursor:
            # Read a single record
            sql = "select message from sisconnect.hello_world where id = %s"
            cursor.execute(sql, (1,))
            result = cursor.fetchone()
            return {"message": result['message'] + " (from Flask)"}


# route test bcrypt
@app.route("/bcrypt")
def test_bcrypt():
    password = 'my password'
    my_hash = bcrypt.generate_password_hash(password)
    verify = bcrypt.check_password_hash(my_hash, password)

    wrong_password = 'my password!'
    wrong_hash = bcrypt.generate_password_hash(password)
    wrong_verify = bcrypt.check_password_hash(wrong_hash, wrong_password)
    return "<p>" + str(my_hash) + "</p><p>" + str(verify) + "</p><p>" + str(wrong_verify) + "</p>"


@app.before_request
def check_authorization():
    no_auth_routes = ["/", "/user/hello", "/user/login"]
    if request.path in no_auth_routes:
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
