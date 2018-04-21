import peewee
import pytest
import playhouse.db_url

from freezegun import freeze_time
from toodles.db import Model, DatabaseManager, TimestampModelMixin

from .conftest import Person

####################################################################
# Model manager test
####################################################################

def test_mm_destroy_tables(dbm):
    dbm.models.destroy_tables()


def test_mm_already_registered(dbm):
    # TODO: needs better exception
    with pytest.raises(AssertionError):
        dbm.models.register(Person)



####################################################################
# Model tests
####################################################################

def test_update_instance(dbm):
    o1 = Person.create(name='hello')
    o1.update_instance(name='world')
    assert o1.refetch().name == 'world'


def test_crud(dbm):
    # ensure writes are working
    o1 = Person.create(name='hello')
    o2 = Person.get(name='hello')
    assert o1.id == o2.id


def test_refetch(dbm):
    o1 = Person.create(name='hello')
    o2 = o1.refetch()
    assert o1 == o2


def test_refetch_does_not_exist(dbm):
    o1 = Person.create(name='hello')
    o1.delete().execute()
    with pytest.raises(Person.DoesNotExist):
        o1.refetch()


def test_create_or_get(dbm):
    o1, created = Person.create_or_get(name='hello')
    assert created is True

    o1, created = Person.create_or_get(name='hello')
    assert created is False


def test_get_or_none(dbm):
    o = Person.get_or_none(name='hello')
    assert o is None

    o1 = Person.create(name='hello')
    o2 = Person.get_or_none(name='hello')
    assert o1 == o2


def test_pk_ref(dbm):
    data = dict(id=99999, name='hello')
    o1 = Person.create(id=99999, name='hello')
    assert o1.to_pk_ref() == data

    o2 = Person.from_pk_ref(data)
    assert o1 == o2


