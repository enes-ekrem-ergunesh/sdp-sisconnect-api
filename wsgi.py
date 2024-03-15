import sys
sys.path.insert(0, './db/')  # Add the DB folder to the Python path

from flask import Flask
import sisConnectDB as scdb

from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Apply CORS for all routes


@app.route("/")
def hello_world():
    connection = scdb.get_connection()
    with connection:
        with connection.cursor() as cursor:
            # Read a single record
            sql = "SELECT `message` FROM `hello_world` WHERE `id`=%s"
            cursor.execute(sql, (1,))
            result = cursor.fetchone()
            return {"message": result['message'] + " (from Flask)"}
