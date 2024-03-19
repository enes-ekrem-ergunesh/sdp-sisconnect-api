from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import db.sisConnectDB as sCDB

app = Flask(__name__)
CORS(app)  # Apply CORS for all routes
bcrypt = Bcrypt(app)


@app.route("/")
def hello_world():
    connection = sCDB.get_connection()
    with connection:
        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT `message` FROM `hello_world` WHERE `id`=%s"
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
