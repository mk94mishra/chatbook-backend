from common.base_model import AbstractBaseModel
from tortoise.fields import ForeignKeyField



class Block(AbstractBaseModel):
    user = ForeignKeyField('models.User', related_name="block_user_id")
    blocked = ForeignKeyField('models.User', related_name="blocked_user_id")

    class Meta:
        table = "tbl_block"
        unique_together = (("user","blocked"), )


      
