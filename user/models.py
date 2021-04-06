from time import time
from common.base_model import AbstractBaseModel
from tortoise.fields import CharField, BooleanField, ForeignKeyField, ForeignKeyRelation, JSONField, IntField


class User(AbstractBaseModel):
    name = CharField(max_length=100, null=True)
    phone = CharField(max_length=100, unique=True)
    password = CharField(max_length=100, null=True)
    gender = CharField(max_length=15, null=True)
    dob = CharField(max_length=50, null=True)
    is_phone_verified = BooleanField(default=False)
    is_deleted = BooleanField(default=False)
    user_type = ForeignKeyField('models.UserType', null=True)
    community = ForeignKeyField('models.Community', null=True)
    profile_pic_url = CharField(max_length=250, null=True)
    is_deleted = BooleanField(default=False)
    inactive_reson = CharField(max_length=500, null=True)
    attribute = JSONField(null=True)

    class Meta:
        table = "tbl_user"



class UserBlocked(AbstractBaseModel):
    user_id = IntField()
    user_id_blocked = IntField()

    class Meta:
        table = "tbl_user_block"
        unique_together = (("user_id","user_id_blocked"), )


        