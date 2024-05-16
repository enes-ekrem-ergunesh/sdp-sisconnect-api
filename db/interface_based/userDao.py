import db.interface_based.baseDao as baseDao


class UserDao(baseDao.BaseDao):
    def __init__(self):
        super(UserDao, self).__init__('users')
