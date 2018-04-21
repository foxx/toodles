import os
import pytest
import peewee

from faker import Faker
from toodles.db import Model, DatabaseManager
from .utils import ResultStore


###############################################################################
# Helpers
###############################################################################

@pytest.fixture
def rs():
    # TODO: there has to be a better solution than this
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    rs = ResultStore(record_mode=True, data_dir=data_dir)
    return rs


###############################################################################
# Fixtures
###############################################################################

@pytest.fixture
def dbm():
    # create manager
    dbm = DatabaseManager()

    # TODO: add support for other databases (see how peewee does it)
    dbm.register('default', 'sqlite:///:memory:')
    dbm.register('other', 'sqlite:///:memory:')

    # de-register all models from previous tests
    # TODO: yucky, needs improvemnet
    for model in [Person, CompoundPerson]:
        if hasattr(model._meta, 'database_manager'):
            delattr(model._meta, 'database_manager')

    # register models
    dbm.models.register(Person)
    dbm.models.register(CompoundPerson)
    dbm.connect()

    # destroy all previous data (why the fuck is this even needed)
    dbm.models.destroy_tables()

    # initialize all tables
    dbm.models.create_tables()

    # generate fake data for all tables
    for model in dbm.models:
        fn = getattr(model, 'generate_test_data', None)
        if fn: fn()

    # handle setup/teardown
    yield dbm
    #dbm.disconnect()


###############################################################################
# Models
###############################################################################

class Person(Model):
    name = peewee.TextField(null=False, unique=True)
    city = peewee.TextField(null=True)

    @classmethod
    def generate_test_data(self):
        """Populate table with fake data for testing"""
        fake = Faker()
        fake.seed(0)

        cities = ['Portland', 'Washington', 'Seattle', 'Mountain View']

        items = []
        for x in range(100):
            city = cities[x % len(cities)]
            items += [dict(name=fake.name(), city=city)]

        with Person._meta.database.atomic():
            Person.insert_many(items).execute()
            assert Person.select().count() == 100


class CompoundPerson(Model):
    first_name = peewee.CharField()
    last_name = peewee.CharField()
    
    class Meta:
        primary_key = peewee.CompositeKey('first_name', 'last_name')

    @classmethod
    def generate_test_data(self):
        """Populate table with fake data for testing"""
        fake = Faker()
        fake.seed(0)

        items = []
        for x in range(100):
            fn, ln = fake.name().split(' ', 1)
            items += [dict(first_name=fn, last_name=ln)]

        with CompoundPerson._meta.database.atomic():
            CompoundPerson.insert_many(items).execute()
            assert CompoundPerson.select().count() == 100



