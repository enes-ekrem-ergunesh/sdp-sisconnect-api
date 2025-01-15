from dao.baseDao import BaseDAO, execute_query


class ProfileFieldDAO(BaseDAO):
    def __init__(self):
        super().__init__('profile_fields', 'sis')

    def get_all_by_profile_id(self, profile_id):
        query = f"SELECT * FROM {self.table} WHERE profile_id = %s"
        return execute_query(query, self.database, (profile_id,))