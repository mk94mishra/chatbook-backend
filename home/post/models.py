from common.base_model import AbstractBaseModel
from tortoise.fields import CharField, BooleanField, ForeignKeyField, JSONField


class Post(AbstractBaseModel):
    user = ForeignKeyField('models.User')
    community = ForeignKeyField('models.Community')
    category = ForeignKeyField('models.Category')
    description = CharField(max_length=5000, null=True)
    media = JSONField(null=True)
    is_spam = BooleanField(default=False)
    is_deleted = BooleanField(default=False)

    class Meta:
        table = "tbl_post"
      
