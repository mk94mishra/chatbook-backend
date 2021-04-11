from tortoise.models import Model
from tortoise.fields import ForeignKeyField, CharField, DatetimeField,IntField, FloatField, BooleanField


class Action(Model):
    type = CharField(max_length=100)

    user = ForeignKeyField('models.User')
    post = ForeignKeyField('models.Post')
    
    description = CharField(max_length=500, null=True)
    media_url = CharField(max_length=500, null=True)

    user_id_blocked = ForeignKeyField('models.User', related_name='blocked_user', null=True)
    user_id_rated = ForeignKeyField('models.User', related_name='rating_receiver', null=True)

    rating = FloatField(default=0, null=True)

    created_at = DatetimeField(auto_now_add=True)

    class Meta:
        table = "tbl_action"
        unique_together = (("user", "post","type"),("user","user_id_blocked"),("user","user_id_rated") )


      
