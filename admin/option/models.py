from common.base_model import AbstractBaseModel
from tortoise.fields import CharField, BooleanField


class Option(AbstractBaseModel):
    name = CharField(max_length=100)
    type = CharField(max_length=100)
    icon_url1 = CharField(max_length=500, null=True)
    icon_url2 = CharField(max_length=500, null=True)
    is_verified = BooleanField(defaul=True)

    class Meta:
        table = "tbl_option"
        unique_together = (("name","type"), )


        