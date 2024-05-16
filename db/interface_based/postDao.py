import db.interface_based.baseDao as baseDao


class PostDao(baseDao.BaseDao):
    def __init__(self):
        super(PostDao, self).__init__('posts')
