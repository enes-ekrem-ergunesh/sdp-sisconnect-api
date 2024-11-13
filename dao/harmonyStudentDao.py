from dao.baseDao import BaseDAO, execute_query_single


class HarmonyStudentDAO(BaseDAO):
    def __init__(self):
        super().__init__('students', 'harmony')

    def get_by_email(self, email):
        query = f"SELECT * FROM {self.table} WHERE email = %s"
        return execute_query_single(query, self.database, (email,))