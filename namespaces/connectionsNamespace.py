from flask import abort, request
from flask_restx import Namespace, Resource, fields
from namespaces.tokenNamespace import get_token_info

import dao.connectionDao as connectionDao
import dao.userDao as userDao

dao = connectionDao.ConnectionDAO()
user_dao = userDao.UserDAO()


ns = Namespace('connections', description='Connection related operations')

connection_info_model = ns.model('Connection Info', {
    'id': fields.Integer(readOnly=True, description='The connection unique identifier'),
    'user_id': fields.Integer(required=True, description='The user id'),
    'connected_user_id': fields.Integer(required=True, description='The connected user id'),
    'accepted_at': fields.DateTime(description='The connection acceptance date'),
    'is_blocked': fields.Boolean(required=True, description='Is the connection blocked?'),
})

connection_post_model = ns.model('Connection Post', {
    'connected_user_id': fields.Integer(required=True, description='The connected user id'),
})

def get_all_connections_of_current_user(user_id):
    connections = dao.get_by_user_id(user_id)
    # filter deleted and blocked ones
    connections = [conn for conn in connections if conn['deleted_at'] is None and not conn['is_blocked']]

    return connections

def get_all_connections_between(user_id, connected_user_id):
    all_connections = get_all_connections_of_current_user(user_id)
    connections = []
    for connection in all_connections:
        if connection['connected_user_id'] == connected_user_id:
            connections.append(connection)
    return connections

def insert_connection(connection):
    if connection['user_id'] == connection['connected_user_id']:
        return abort(400, "Cannot connect to yourself")
    connections = dao.get_by_user_id(connection['user_id'])
    # filter deleted ones
    connections = [conn for conn in connections if conn['deleted_at'] is None]
    for conn in connections:
        if conn['connected_user_id'] == connection['connected_user_id']:
            if conn['is_blocked'] == 1:
                return abort(400, "User is blocked")
            else:
                return abort(400, "Connection already exists")

    return dao.create(connection)

def remove_connection(user_id, connected_user_id):
    connections = get_all_connections_between(user_id, connected_user_id)
    for conn in connections:
        if conn:
            dao.soft_delete(conn['id'])
    return "Connection removed"

def block_user(user_id, connected_user_id):
    to_be_blocked_connection_id = 0
    connections = get_all_connections_between(user_id, connected_user_id)
    # If there are no connections, create one
    if not connections:
        to_be_blocked_connection_id = insert_connection({
            'user_id': user_id,
            'connected_user_id': connected_user_id
        })

    connections.append(dao.get_by_id(to_be_blocked_connection_id))

    for conn in connections:
        if conn:
            dao.block_user(conn['id'])

    return "User blocked"

def unblock_user(user_id, connected_user_id):
    connections = dao.get_blocked_connections_by_user_id(user_id)
    for conn in connections:
        if conn['connected_user_id'] == connected_user_id:
            if conn:
                dao.soft_delete(conn['id'])
    return "User unblocked"

@ns.route('/')
class Connections(Resource):
    @ns.doc('list_connections')
    @ns.marshal_list_with(connection_info_model)
    def get(self):
        """Get all connections of current user"""
        token = request.headers.get('Authorization')
        token_info = get_token_info(token)
        connections = get_all_connections_of_current_user(token_info['user_id'])
        if not connections:
            return []
        return connections

    @ns.doc('create_connection')
    @ns.expect(connection_post_model)
    def post(self):
        """Create a new connection"""
        token = request.headers.get('Authorization')
        token_info = get_token_info(token)
        user_id = token_info['user_id']
        data = request.json
        connected_user_id = data['connected_user_id']
        connection = {
            'user_id': user_id,
            'connected_user_id': connected_user_id
        }
        return insert_connection(connection)

@ns.route('/<int:connected_user_id>')
class Connection(Resource):
    @ns.doc('get_connection_with_connected_user')
    @ns.marshal_with(connection_info_model)
    def get(self, connected_user_id):
        """Get connection with connected user"""
        token = request.headers.get('Authorization')
        token_info = get_token_info(token)
        connection = dao.get_by_connected_user_id_and_user_id(connected_user_id, token_info['user_id'])
        if not connection or connection['deleted_at']:
            return None
        return connection

    @ns.doc('remove_connection')
    def delete(self, connected_user_id):
        """Remove a connection"""
        token = request.headers.get('Authorization')
        token_info = get_token_info(token)
        user_id = token_info['user_id']
        return remove_connection(user_id, connected_user_id)

@ns.route('/block/')
class ConnectionBlock(Resource):
    @ns.doc('list_blocked_connections')
    @ns.marshal_list_with(connection_info_model)
    def get(self):
        """Get all blocked connections of current user"""
        token = request.headers.get('Authorization')
        token_info = get_token_info(token)
        connections = dao.get_blocked_connections_by_user_id(token_info['user_id'])
        if not connections:
            return []
        return connections

    @ns.doc('block_user')
    @ns.expect(connection_post_model)
    def put(self):
        """Block a user"""
        token = request.headers.get('Authorization')
        token_info = get_token_info(token)
        user_id = token_info['user_id']
        data = request.json
        connected_user_id = data['connected_user_id']
        return block_user(user_id, connected_user_id)

@ns.route('/unblock/')
class ConnectionUnblock(Resource):
    @ns.doc('unblock_user')
    @ns.expect(connection_post_model)
    def put(self):
        """Unblock a user"""
        token = request.headers.get('Authorization')
        token_info = get_token_info(token)
        user_id = token_info['user_id']
        data = request.json
        connected_user_id = data['connected_user_id']
        return unblock_user(user_id, connected_user_id)
