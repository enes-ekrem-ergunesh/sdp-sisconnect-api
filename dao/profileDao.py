from dao.baseDao import BaseDAO, execute_query_single


class ProfileDAO(BaseDAO):
    def __init__(self):
        super().__init__('profiles', 'sis')

    def get_by_user_id(self, user_id):
        query = f"SELECT * FROM {self.table} WHERE user_id = %s"
        return execute_query_single(query, self.database, (user_id,))