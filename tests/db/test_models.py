import peewee
import pytest
import playhouse.db_url

from freezegun import freeze_time
from toodles.db import Model, DatabaseManager, TimestampModelMixin


###############################################################################
# Fixtures and bases
###############################################################################

class Person(Model):
    name = peewee.TextField(null=True)

 
class PlayModelBase(Model):
    class Meta:
        db_table = 'test_model'


@pytest.fixture
def PlayModel(dbm):
   
    assert PlayModel._meta.database == dbm['default']
    dbm.models.register(PlayModel)
    dbm.models.create_tables()
    return PlayModel


####################################################################
# Model manager test
####################################################################

def test_mm_destroy_tables(dbm, PlayModel):
    dbm.models.destroy_tables()

def test_mm_already_registered(dbm, PlayModel):
    with pytest.raises(RuntimeError):
        dbm.models.register(PlayModel)



####################################################################
# Model tests
####################################################################

def test_update_instance(dbm, PlayModel):
    o1 = PlayModel.create(name='hello')
    o1.update_instance(name='world')
    assert o1.refetch().name == 'world'


def test_crud(dbm, PlayModel):
    # ensure writes are working
    o1 = PlayModel.create(name='hello')
    o2 = PlayModel.get(name='hello')
    assert o1.id == o2.id


def test_refetch(dbm, PlayModel):
    o1 = PlayModel.create(id=1)
    o2 = o1.refetch()
    assert o1 == o2


def test_refetch_does_not_exist(dbm, PlayModel):
    o1 = PlayModel.create(id=1)
    o1.delete().execute()
    with pytest.raises(PlayModel.DoesNotExist):
        o1.refetch()


def test_create_or_get(dbm, PlayModel):
    o1, created = PlayModel.create_or_get(id=1)
    assert created is True

    o1, created = PlayModel.create_or_get(id=1)
    assert created is False


def test_get_or_none(dbm, PlayModel):
    o = PlayModel.get_or_none(id=1)
    assert o is None

    o1 = PlayModel.create(id=1)
    o2 = PlayModel.get_or_none(id=1)
    assert o1 == o2


def test_cursor_ref(dbm, PlayModel):
    data = dict(id=1)
    o1 = PlayModel.create(id=1)
    assert o1.to_cursor_ref() == data

    o2 = PlayModel.from_cursor_ref(data)
    assert o1 == o2


