from tortoise.models import Model
from tortoise.fields import CharField


class Faq(Model):
    title = CharField(max_length=500, unique=True)
    description = CharField(max_length=5000)

    class Meta:
        table = "tbl_faq"
      
