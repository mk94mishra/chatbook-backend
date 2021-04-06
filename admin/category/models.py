from common.base_model import AbstractBaseModel
from tortoise.fields import CharField, ForeignKeyField


class Category(AbstractBaseModel):
    name = CharField(max_length=100, unique=True)
    icon_url = CharField(max_length=500)

    class Meta:
        table = "tbl_category"
      
