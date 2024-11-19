from dao.baseDao import BaseDAO, execute_query_single


class TokenDAO(BaseDAO):
    def __init__(self):
        super().__init__('tokens', 'sis')

    def get_by_token(self, token):
        query = f"SELECT * FROM {self.table} WHERE token = %s"
        return execute_query_single(query, self.database, (token,))