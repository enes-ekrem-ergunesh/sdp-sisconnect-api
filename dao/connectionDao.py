from dao.baseDao import BaseDAO, execute_query, execute_query_single


class ConnectionDAO(BaseDAO):
    def __init__(self):
        super().__init__('connections', 'sis')

    def get_by_user_id(self, user_id):
        query = f"SELECT * FROM {self.table} WHERE user_id = %s"
        return execute_query(query, self.database, (user_id,))

    def get_by_connected_user_id_and_user_id(self, connected_user_id, user_id):
        query = f"SELECT * FROM {self.table} WHERE connected_user_id = %s AND user_id = %s AND deleted_at IS NULL"
        return execute_query_single(query, self.database, (connected_user_id, user_id))

    def block_user(self, connection_id):
        query = f"UPDATE {self.table} SET is_blocked = TRUE WHERE id = %s"
        return execute_query(query, self.database, (connection_id,))

    def get_blocked_connections_by_user_id(self, user_id):
        query = f"SELECT * FROM {self.table} WHERE user_id = %s AND is_blocked = TRUE AND deleted_at IS NULL"
        return execute_query(query, self.database, (user_id,))