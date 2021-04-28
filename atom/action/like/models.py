from common.base_model import AbstractBaseModel
from tortoise.fields import ForeignKeyField


class LikePost(AbstractBaseModel):
    post = ForeignKeyField('models.Post')
    user = ForeignKeyField('models.User')

    class Meta:
        table = "tbl_like_post"
        unique_together = (("post","user"), )

class LikeComment(AbstractBaseModel):
    comment = ForeignKeyField('models.Option')
    user = ForeignKeyField('models.User')

    class Meta:
        table = "tbl_like_comment"
        unique_together = (("comment","user"), )

      
