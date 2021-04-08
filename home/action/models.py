from tortoise.models import Model
from tortoise.fields import ForeignKeyField, CharField, DatetimeField


class ActionPost(Model):
    user = ForeignKeyField('models.User')
    post = ForeignKeyField('models.Post')
    type = CharField(max_length=100)
    
    description = CharField(max_length=500, null=True)
    media_url = CharField(max_length=500, null=True)

    created_at = DatetimeField(auto_now_add=True)

    class Meta:
        table = "tbl_action_home"
        unique_together = (("user", "post","type"), )


      
