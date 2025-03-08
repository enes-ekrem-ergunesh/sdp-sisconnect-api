from dao.baseDao import BaseDAO, execute_update, execute_query, execute_query_single


class PostLikeDAO(BaseDAO):
    def __init__(self):
        super().__init__('post_likes', 'sis')

    def like_count(self, post_id):
        query = f"SELECT COUNT(*) FROM {self.table} WHERE post_id = %s AND deleted_at IS NULL"
        return execute_query_single(query, self.database, post_id)

    def get_users_liked_post(self, post_id):
        query = f"SELECT u.* FROM {self.table} pl JOIN users u ON pl.user_id = u.id WHERE pl.post_id = %s AND pl.deleted_at IS NULL group by u.id"
        return execute_query(query, self.database, post_id)

    def get_by_post_id_and_user_id(self, post_id, user_id):
        query = f"SELECT * FROM {self.table} WHERE post_id = %s AND user_id = %s AND deleted_at IS NULL"
        return execute_query(query, self.database, (post_id, user_id))

    def remove_like(self, post_id, user_id):
        query = f"UPDATE {self.table} SET deleted_at = NOW() WHERE user_id = %s AND post_id = %s AND deleted_at IS NULL"
        return execute_update(query, self.database, (user_id, post_id))
