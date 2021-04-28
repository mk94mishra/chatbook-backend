from common.base_model import AbstractBaseModel
from tortoise.fields import ForeignKeyField


class Bookmark(AbstractBaseModel):
    post = ForeignKeyField('models.Post')
    user = ForeignKeyField('models.User')

    class Meta:
        table = "tbl_bookmark"
        unique_together = (("post","user"), )


      
