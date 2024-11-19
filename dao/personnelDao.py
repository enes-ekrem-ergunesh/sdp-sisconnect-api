from dao.baseDao import BaseDAO


class PersonnelDAO(BaseDAO):
    def __init__(self):
        super().__init__('personnels', 'sis')