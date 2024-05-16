import db.interface_based.baseDao as baseDao


class CommentDao(baseDao.BaseDao):
    def __init__(self):
        super(CommentDao, self).__init__('comments')
