from flask import jsonify, make_response, abort


def http_response(status_code, message):
    abort(make_response(jsonify({'message': message}), status_code))
