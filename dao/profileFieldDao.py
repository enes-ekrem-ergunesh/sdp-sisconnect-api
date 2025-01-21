from dao.baseDao import BaseDAO, execute_query


class ProfileFieldDAO(BaseDAO):
    def __init__(self):
        super().__init__('profile_fields', 'sis')

    def get_all_by_profile_id(self, profile_id):
        query = f"SELECT t1.*, t2.name AS 'profile_field_type', t2.data_type AS 'profile_field_data_type' FROM {self.table} t1 JOIN profile_field_types t2 ON t1.profile_field_type_id = t2.id WHERE profile_id = %s "
        return execute_query(query, self.database, (profile_id,))