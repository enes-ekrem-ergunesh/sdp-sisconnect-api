from flask import abort, request
from flask_restx import Namespace, Resource, fields
from namespaces.tokenNamespace import get_token_info

import dao.postDao as postDao
import dao.userDao as userDao

dao = postDao.PostDAO()
user_dao = userDao.UserDAO()


ns = Namespace('posts', description='Post related operations')

post_info_model = ns.model('Post Info', {
    'id': fields.Integer(readOnly=True, description='The connection unique identifier'),
    'user_id': fields.Integer(required=True, description='The user id'),
    'content': fields.String(required=True, description='The post content'),
    'created_at': fields.DateTime(readOnly=True, description='The connection creation date'),
})

post_post_model = ns.model('Post Post', {
    'content': fields.String(required=True, description='The post content'),
})

def get_all_posts_of_current_user(user_id):
    return dao.get_by_user_id(user_id)

def create_post(content, user_id):
    data = {
        'content': content,
        'user_id': user_id
    }
    return dao.create(data)

def remove_post(user_id, post_id):
    post = dao.get_by_id(post_id)
    if not post:
        abort(404, 'Post not found')
    elif post['user_id'] != user_id:
        abort(400, 'Unauthorized')
    else:
        dao.soft_delete(post_id)
        return {'message': 'Post removed'}

@ns.route('/')
class Posts(Resource):
    @ns.doc('list_posts')
    @ns.marshal_list_with(post_info_model)
    def get(self):
        """Get all posts of current user"""
        token = request.headers.get('Authorization')
        token_info = get_token_info(token)
        posts = get_all_posts_of_current_user(token_info['user_id'])
        if not posts:
            return []
        return posts

    @ns.doc('create_post')
    @ns.expect(post_post_model)
    def post(self):
        """Create a new post"""
        token = request.headers.get('Authorization')
        token_info = get_token_info(token)
        data = request.json
        return create_post(data['content'], token_info['user_id'])

@ns.route('/<int:post_id>')
class Post(Resource):
    @ns.doc('get_post')
    @ns.marshal_with(post_info_model)
    def get(self, post_id):
        """Get post by id"""
        post = dao.get_by_id(post_id)
        if not post or post['deleted_at']:
            return None
        return post

    @ns.doc('remove_post')
    def delete(self, post_id):
        """Remove a connection"""
        token = request.headers.get('Authorization')
        token_info = get_token_info(token)
        user_id = token_info['user_id']
        return remove_post(user_id, post_id)

@ns.route('/connected')
class ConnectedPosts(Resource):
    @ns.doc('list_posts_of_connected')
    @ns.marshal_list_with(post_info_model)
    def get(self):
        """Get all posts of connected users"""
        token = request.headers.get('Authorization')
        token_info = get_token_info(token)
        posts = dao.get_all_connected(token_info['user_id'])
        if not posts:
            return []
        return posts