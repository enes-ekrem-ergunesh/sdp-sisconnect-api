from dao.baseDao import BaseDAO, execute_query_single


class HarmonyPersonnelDAO(BaseDAO):
    def __init__(self):
        super().__init__('personnels', 'harmony')

    def get_by_email(self, email):
        query = f"SELECT * FROM {self.table} WHERE school_email = %s"
        return execute_query_single(query, (email,))