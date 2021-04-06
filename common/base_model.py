from time import time
import datetime
from tortoise import Model
from tortoise.fields import UUIDField, IntField, BooleanField, ForeignKeyField,DatetimeField


class AbstractBaseModel(Model):
    id = IntField(pk=True)
    created_at = DatetimeField(auto_now_add=True)
    updated_at = DatetimeField(auto_now=True)
    is_active = BooleanField(default=True)
    created_by = IntField(null=True)
    updated_by = IntField(null=True)

    class Meta:
        abstract = True
