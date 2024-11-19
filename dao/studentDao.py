from dao.baseDao import BaseDAO


class StudentDAO(BaseDAO):
    def __init__(self):
        super().__init__('students', 'sis')