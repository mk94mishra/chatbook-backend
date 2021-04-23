from tortoise.models import Model
from tortoise.fields import ForeignKeyField, CharField, DatetimeField,IntField, FloatField, BooleanField, JSONField


class Action(Model):
    type = CharField(max_length=100)
    user = ForeignKeyField('models.User')

    data = JSONField(null=True)

    created_at = DatetimeField(auto_now_add=True)

    class Meta:
        table = "tbl_action"
       


      
