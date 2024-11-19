from flask_restx import Namespace, Resource, fields
import dao.tokenDao as tokenDao

dao = tokenDao.TokenDAO()

ns = Namespace('tokens', description='Token related operations')

token_info = ns.model('Token Info', {
    'id': fields.Integer(readOnly=True, description='The user unique identifier'),
    'token': fields.String(required=True, description='The token'),
    'user_id': fields.Integer(required=True, description='The user id'),
    'valid_until': fields.DateTime(required=True, description='The token expiration date'),
    'revoked_at': fields.DateTime(description='The token revocation date'),
})

token = ns.model('Token', {
    'token': fields.String(required=True, description='The token'),
})


@ns.route('/')
class TokenInfo(Resource):
    @ns.doc('get_token_info')
    @ns.expect(token)
    @ns.marshal_with(token_info)
    def post(self):
        """Get token info"""
        data = ns.payload
        print(data)
        response = dao.get_by_token(data['token'])
        if not response:
            ns.abort(404, "Token not found")
        return response