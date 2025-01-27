from dao.baseDao import BaseDAO, execute_query


class PostDAO(BaseDAO):
    def __init__(self):
        super().__init__('posts', 'sis')

    def get_by_user_id(self, user_id):
        query = f"SELECT * FROM {self.table} WHERE user_id = %s AND deleted_at IS NULL order by created_at desc"
        return execute_query(query, self.database, (user_id,))

    def get_all_connected(self, user_id):
        query = f"select * from posts p join connections c on c.connected_user_id = p.user_id where c.user_id = %s and c.deleted_at is null and p.deleted_at is null and c.is_blocked = 0 order by p.created_at desc"
        return execute_query(query, self.database, (user_id,))
