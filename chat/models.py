from tortoise.models import Model
from tortoise.fields import CharField, BooleanField, ForeignKeyField, DatetimeField


class Chat(Model):
    group_id = CharField(max_length=100)
    sender = ForeignKeyField('models.User', related_name='sender_id')
    receiver = ForeignKeyField('models.User', related_name='receiver_id')
    msg = CharField(max_length=2000)
    created_at = DatetimeField(auto_now_add=True)
    is_seen_min = BooleanField(null=True)
    is_seen_max = BooleanField(null=True)
    is_deleted_min = BooleanField(default=False)
    is_deleted_max = BooleanField(default=False)


    class Meta:
        table = "tbl_chat_msg"
