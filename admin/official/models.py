from tortoise.models import Model
from tortoise.fields import CharField, JSONField


class Official(Model):
    title = CharField(max_length=100)
    description = CharField(max_length=5000)

    class Meta:
        table = "tbl_official"
      
