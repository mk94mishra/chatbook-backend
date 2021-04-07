from tortoise.models import Model
from tortoise.fields import ForeignKeyField, FloatField,DatetimeField


class Rating(Model):
    user = ForeignKeyField('models.User', related_name='rating_giver')
    user_id_rated = ForeignKeyField('models.User', related_name='rating_receiver')
    rating = FloatField(default=0)
    created_at = DatetimeField(auto_now_add=True)
    #updated_at = DatetimeField(null=True)
    class Meta:
        table = "tbl_rating"
        unique_together = (("user_id","user_id_rated"), )

      
