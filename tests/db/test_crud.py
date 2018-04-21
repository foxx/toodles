import os
import pickle

import peewee
import pytest
import playhouse
import toodles

from pprint import pprint
from tabulate import tabulate
from toodles.db import PrimaryKeyPagination


####################################################################
# Test CRUD
####################################################################


class TestPrimaryKeyPagination:
    
    def generate(self, *args, **kwargs):
        query = PrimaryKeyPagination.paginate_query(*args, **kwargs)
        return [ r.__data__ for r in query ]

    def test_limit(self, dbm):
        """Test query limiting"""
        query = Person.select()

        # 100 items, no offset, no user sorting
        results = self.generate(query=query, offset=None, count=100)
        expected = rs.check('test_limit_1', results)
        assert results == expected

        # 50 items, no offset, no user sorting
        results = self.generate(query=query, offset=None, count=50)
        assert len(results) == 50
        expected = rs.check('test_limit_2', results)
        assert results == expected

    def test_sort(self, dbm):
        query = Person.select()

        # 100 items, no offset, sort by name(asc)
        sort = [('name', 'asc')]
        results = self.generate(query=query, offset=None, count=100, sort=sort)
        expected = rs.check('test_sort_1', results)
        assert results == expected
 
        # 100 items, no offset, sort by name(desc)
        sort = [('name', 'desc')]
        results = self.generate(query=query, offset=None, count=100, sort=sort)
        expected = rs.check('test_sort_2', results)
        assert results == expected

        # 100 items, no offset, sorted
        sort = [('city', 'asc'), ('name', 'asc')]
        results = self.generate(query=query, offset=None, count=100, sort=sort)
        expected = rs.check('test_sort_3', results)
        assert results == expected

        # 100 items, no offset, sorted
        sort = [('city', 'asc'), ('name', 'desc')]
        results = self.generate(query=query, offset=None, count=100, sort=sort)
        expected = rs.check('test_sort_4', results)
        assert results == expected

    def test_offset(self, dbm):
        query = Person.select()

        # 100 items (expect 50), offset 50, sort by name(asc)
        sort = [('name', 'asc')]
        results = self.generate(query=query, offset=51, count=100, sort=sort)
        assert len(results) == 50
        expected = rs.check('test_offset_1', results)
        assert results == expected

        # 100 items (expect 50), offset 50, no sort (defaults to pk sort)
        results = self.generate(query=query, offset=51, count=100)
        assert len(results) == 50
        expected = rs.check('test_offset_2', results)
        assert results == expected

        #print(tabulate(results, headers="keys")); assert False


