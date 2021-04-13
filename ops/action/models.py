from tortoise.models import Model
from tortoise.fields import ForeignKeyField, CharField, DatetimeField,IntField, FloatField, BooleanField


class Action(Model):
    type = CharField(max_length=100)
    user = ForeignKeyField('models.User')

    # like, bookmark,spam,comment
    post = ForeignKeyField('models.Post', null=True)

    # comment & spam
    description = CharField(max_length=500, default=1,null=True)
    # comment
    media_url = CharField(max_length=500, default=1,null=True)
    # comment - like
    comment_id = IntField(null=True)

    # user block
    user_id_blocked = ForeignKeyField('models.User', related_name='blocked_user', null=True)
    # user rated
    user_id_rated = ForeignKeyField('models.User', related_name='rating_receiver', null=True)
    rating = FloatField(default=0, null=True)

    created_at = DatetimeField(auto_now_add=True)

    class Meta:
        table = "tbl_action"
        unique_together = (("user", "post", "description", "media_url","type"),("user","comment_id"),("user","user_id_blocked"),("user","user_id_rated") )


      
