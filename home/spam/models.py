from common.base_model import AbstractBaseModel
from tortoise.fields import ForeignKeyField,CharField


class Spam(AbstractBaseModel):
    post = ForeignKeyField('models.Post')
    user = ForeignKeyField('models.User')
    reason = CharField(max_length=2000, null=True)

    class Meta:
        table = "tbl_spam"


      
