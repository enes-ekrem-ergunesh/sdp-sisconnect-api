from dao.baseDao import BaseDAO, execute_query_single


class HarmonyStudentDAO(BaseDAO):
    def __init__(self):
        super().__init__('students', 'harmony')

    def get_by_email(self, email):
        query = f"SELECT * FROM {self.table} WHERE email = %s"
        return execute_query_single(query, self.database, (email,))

    def search(self, search_term):
        query = f"SELECT * FROM {self.table} WHERE CONCAT(first_name, ' ', family_name) LIKE %s first_name LIKE %s OR family_name LIKE %s OR email LIKE %s"
        return execute_query_single(query, self.database, (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%", f"%{search_term}%"))