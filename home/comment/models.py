from common.base_model import AbstractBaseModel
from tortoise.fields import CharField, BooleanField, DatetimeField, ForeignKeyField, IntField


class Comment(AbstractBaseModel):
    post = ForeignKeyField('models.Post')
    user = ForeignKeyField('models.User')
    description = CharField(max_length=500, null=True)
    media_type = CharField(max_length=50, null=True)
    media_url = CharField(max_length=500, null=True)
    is_spam = BooleanField(default=False)
    is_deleted = BooleanField(default=False)

    class Meta:
        table = "tbl_comment"
      
