from dao.baseDao import BaseDAO


class ProfileFieldTypeDAO(BaseDAO):
    def __init__(self):
        super().__init__('profile_field_types', 'sis')