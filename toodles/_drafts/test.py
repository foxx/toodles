import pytest
from urllib.parse import parse_qsl


def coerce(value):
    """
    TODO
    """


def test_all():

    with pytest.raises(ValueError):
        # TODO: needs test of error message
        convert('filter.=lalal')


    items = [
        "filter.age=between:1,20",
        "filter.age=12&filter.age.lala=13&lalala=2",
        "filter.age=in:20,21,23",
        "filter.age=gt:20",
        "filter.age=gte:20",
        "filter.age=lt:20",
        "filter.age=lte:20",
        "filter.name=Bob&filter.friend.name=John&filter.age=gte:42",
        "filter.full_name=Bob Bobinsky&filter.occupation=in:Mice Circus Owner,gentleman",
        "filter.name=bob,glob,sam",
        "filter.age=between:20,32.13"]

    for i in items:
        print(convert(i))

    assert False


def convert(qs, namespace:str='filter', sep='.', modsep=':'):
    """
    TODO: between should split values? and only check for two?
    TODO: values should be casted based on hinting? e.g. try to cast to Decimal, int and string
    """

class Filters:
    def __init__(self, field_ns:str='filter', field_sep='.', modsep=':'):
        self.field_ns = field_ns
        self.field_sep = field_sep
        self.modsep = modsep

    def convert(self):
        parts = parse_qsl(qs)
        keysep = namespace+sep

        # look for filters in our namespace
        filters = []
        for k,v in parts:
            # clean up values
            v = v.strip()
            k = k.strip()

            # skip past any fields that are not in our namespace
            if not k.startswith(keysep): continue

            # verify keyspace
            nkey = k.split(keysep,1)[1]
            if not nkey:
                raise ValueError("Invalid field '{}'".format(k))

            # split key with dot notation
            nkey = nkey.split(sep)

            # check for modifier
            mod = None
            modifiers = ['between', 'in', 'gt', 'gte', 'lt', 'lte', 'contains', 'exact']
            nvalue = v
            if ':' in v:
                mod, nvalue = v.split(':', 1)

            o = dict(key=nkey, modifier=mod, value=nvalue)
            filters += [o]

    return filters

