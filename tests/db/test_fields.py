import peewee
import datetime
from toodles.db import (Model, DatabaseManager, TimestampModelMixin)


####################################################################
# Field tests
####################################################################

def test_timestamp_model(dbm):
    @dbm.models.register
    class PlayModel(TimestampModelMixin):
        name = peewee.TextField(null=True)

    dbm.models.create_tables()
 
    dt = datetime.datetime(2018, 1, 1, 0, 0, 0)
    with freeze_time(dt):
        o1 = PlayModel.create(name='hello')
        assert o1.created == dt

