from flask import request
from flask_restx import Namespace, Resource
from namespaces.tokenNamespace import get_token_info
from namespaces.profileNamespace import profile_info_model, collect_profile_info_by_user

import dao.postLikeDao as postLikeDao
import dao.userDao as userDao
import dao.postDao as postDao

dao = postLikeDao.PostLikeDAO()
user_dao = userDao.UserDAO()
post_dao = postDao.PostDAO()


ns = Namespace('postlikes', description='Post like related operations')

def like(post_id, user_id):
    existing_like = dao.get_by_post_id_and_user_id(post_id, user_id)
    if existing_like:
        return {'message': 'Already liked'}
    data = {
        'post_id': post_id,
        'user_id': user_id
    }
    dao.create(data)
    return {'message': 'Liked'}

def remove_like(post_id, user_id):
    return dao.remove_like(post_id, user_id)

@ns.route('/<int:post_id>')
class PostLikes(Resource):
    @ns.doc('like_post')
    def post(self, post_id):
        """Like the post"""
        token = request.headers.get('Authorization')
        token_info = get_token_info(token)
        return like(post_id, token_info['user_id'])

    @ns.doc('remove_like_from_post')
    def delete(self, post_id):
        """Remove like from the post"""
        token = request.headers.get('Authorization')
        token_info = get_token_info(token)
        remove_like(post_id, token_info['user_id'])
        return {'message': 'Like removed'}

    @ns.doc('get_like_count')
    def get(self, post_id):
        """Get like count of the post"""
        return dao.like_count(post_id)

@ns.route('/<int:post_id>/users')
class PostLikeUsers(Resource):
    @ns.doc('get_users_liked_post')
    @ns.marshal_list_with(profile_info_model)
    def get(self, post_id):
        """Get users who liked the post"""
        users = dao.get_users_liked_post(post_id)
        profiles = []
        for user in users:
            profiles.append(collect_profile_info_by_user(user))
        return profiles

