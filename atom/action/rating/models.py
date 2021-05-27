from common.base_model import AbstractBaseModel
from tortoise.fields import ForeignKeyField,FloatField


class Rating(AbstractBaseModel):
    user = ForeignKeyField('models.User', related_name="rating_user_id")
    user_rated = ForeignKeyField('models.User', related_name="rated_user_id")
    rating = FloatField(default=0)

    class Meta:
        table = "tbl_rating"
        unique_together = (("user","user_rated"), )

      
