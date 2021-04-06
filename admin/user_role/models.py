from common.base_model import AbstractBaseModel
from tortoise.fields import CharField


class UserRole(AbstractBaseModel):
    name = CharField(max_length=100, unique=True)

    class Meta:
        table = "tbl_user_role"



        
      
