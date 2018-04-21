import os
import pytest
import peewee

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

    # register models
    dbm.models.register(Person)
    dbm.models.register(CompoundPerson)

    # initialize all tables
    dbm.connect()
    dbm.models.create_tables()

    # generate fake data for all tables
    for model in dbm.models:
        fn = getattr(model, 'generate_test_data', None)
        if fn: fn()

    # handle setup/teardown
    yield dbm
    dbm.disconnect()

    # remove all models from this manager
    dbm.models.deregister_all()


###############################################################################
# Models
###############################################################################

class Person(Model):
    name = peewee.TextField(null=False)
    city = peewee.TextField(null=False)

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
        Person.insert_many(items).execute()
        assert Person.select().count() == 100


class CompoundPerson(Model):
    first_name = peewee.CharField()
    last_name = peewee.CharField()
    
    class Meta:
        primary_key = peewee.CompositeKey("field1", "field2")

    @classmethod
    def generate_test_data(self):
        """Populate table with fake data for testing"""
        fake = Faker()
        fake.seed(0)

        items = []
        for x in range(100):
            fn, ln = faker.Faker().name().split(' ', 1)
            items += [dict(first_name=fn, last_name=ln)]
        CompoundPerson.insert_many(items).execute()
        assert CompoundPerson.select().count() == 100



