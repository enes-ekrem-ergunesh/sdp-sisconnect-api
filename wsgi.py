from flask import Flask
from flask_restx import Api

from namespaces.userNamespace import ns as user_namespace
from namespaces.harmonyPersonnelNamespace import ns as harmony_personnel_namespace
from namespaces.harmonyStudentNamespace import ns as harmony_student_namespace
from namespaces.tokenNamespace import ns as token_namespace

app = Flask(__name__)
api = Api(app, version='1.0', title='SIS Connect API',
    description='A simple API',
)

api.add_namespace(user_namespace)
api.add_namespace(harmony_personnel_namespace)
api.add_namespace(harmony_student_namespace)
api.add_namespace(token_namespace)

if __name__ == '__main__':
    app.run(debug=True)