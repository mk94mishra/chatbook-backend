from common.base_model import AbstractBaseModel
from tortoise.fields import CharField


class OrderBy(AbstractBaseModel):
    name_backend = CharField(max_length=100)
    name_frontend = CharField(max_length=100)
    type = CharField(max_length=100)

    class Meta:
        table = "tbl_orderby"
      
