import pytest
import peewee

from toodles import Toodles
from toodles.db import Model
from toodles.web import View


###############################################################################
# Base application
###############################################################################

app = Toodles()


###############################################################################
# Models
###############################################################################

@app.models.register
class Person(Model):
    name = peewee.CharField()
    email = peewee.CharField()
    phone_number = peewee.CharField()
    group = peewee.IntegerField()


###############################################################################
# Views
###############################################################################



class Pagination:
    pass



class ListView(View):
    # which fields user can sort on
    sort_fields = None

    # which fields user can filter on
    filter_fields = None

    # which permissions user needs to access
    permissions = None

    # which marshmallow schema should this list use
    serializer = None

    # which pagination should this use?
    pagination = None

    # query string field to use for sorting
    qs_sort_key = 'sort'

    def get_request_filter(self):
        """
        Returns filter parameters from request query string

        # allow all filters
        filter_fields = ['field1', 'field2']

        ?filter[field1]=lalal&filter[field2.gt]=36

        For example:
        ?filter[field1][gt]=lalala&
         filter[field2][gte]
        """

    def convert_sort_string(self):
        """
        Convert sort string to sorting pairs

        >>> convert_sort_string('field1,+field2,-field3')
        [('field1', 'desc'), ('field2', 'asc'), ('field3', 'desc')]
        """

        values = [ v.strip() for v in values.split(',') ]
        sort = []
        for value in values:
            direction = 'asc'

            if value[0] == '+':
                direction = 'asc'
                value = value[1:]

            elif value[0] == '-':
                direction = 'desc'
                value = value[1:]

            elif value[0] not in string.ascii_lowercase + string.digits:
                raise ValueError("Invalid sort field: '{}'".format(value))

            sort += [(value, direction)]
        
        return sort

    def dispatch(self):
        # convert sort parameters from query string
        sort_value = request.query.get(self.qs_sort_key)
        sort_params = self.convert_sort_string(sort_value)

        # convert filter parameters from query string

    def convert_filter_string(self, value):
        """
        ?filter[field1]=a&filter[field2.gte]=83
        ?filter=field1>lalala,field2>=55
        ?filter[field1]=blah&filter[field2]=gte(1)

        ?filter.field1.gte=123&filter.field2=hello
        ?filter[field1][gte]=123&filter[field2]=hello
        ?filter[field1.gte]=123&filter[field2]hello
        ?filter.field1>=123&filter.field2=hello&filter.field3>66
        
        ?filter.field1.gte=123&filter.field2=hello&filter.field3.lte=123

        https://api.roak.io/people?filter.country=gb
        https://api.roak.io/people?filter.country=gb&filter.lang=en&filter.gender=female&filter.name.contains=kitty
        https://api.roak.io/people?filter.country=gb&filter.gender=female,male&filter.age=21,40

        ?filter.age.gte=23
        ?filter.age=gte(23)

        ?filter.age.between=21,40
        ?filter.age=between(21,40)

        ?filter.name=contains(hello)
        ?filter.name.contains=hello

        https://api.roak.io/people?filter.name.contains=mary
        https://api.roak.io/people?filter.name=contains(mary)
        https://api.roak.io/people?name=mary

        ?filter.name=contains:mary
        ?filter.name=in:mary,alex,jessica&filter.age=between:21,40&filter.country=in:uk,us,es
        ?filter.age=between:21,40
        ?filter.age=gte:21
        ?filter.age=lt:21
        ?filter.age=40

        Supported modifiers: lt,lte,gt,gte,contains,exact,in
        (if no modifier provided, default to 'contains')

        """


    def get_request_sort(self):
        """
        Returns sorting parameters from request query string

        """
        values = request.query.getall('sort')
        return self.convert_sort_string(values)

        '''
    def get_request_sort(self):
        """
        Returns sorting parameters from request query string

        For example:
        ?sort=field1,+field2,-field3
        ?sort=field1&sort=field2,asc&sort=field3,desc 
        """
        # TODO: implement unit test

        # split sorting into field/direction pairs
        values = request.query.getall('sort')
        values = [ pad(value.split(','), 2, '') for value in values ]

        # clean up each pair
        values = [ [ f.lower().strip() for f in value ] for value in values ]

        # check each pair
        VALID_DIRECTIONS = ['asc', 'desc']
        DEFAULT_DIRECTION = 'asc'
        sort = []
        for field, direction in values:
            # field must be specified
            if not field:
                raise ValueError("Invalid sort parameters (field is empty)")

            # only allow sorting on allowed fields
            if field not in self.sort_fields:
                raise ValueError(
                    "Invalid sort parameters (field '{}' not allowed)"
                    .format(field))

            # direction must be valid
            direction = direction if direction else DEFAULT_DIRECTION
            if direction not in VALID_DIRECTIONS:
                raise ValueError("Invalid sort direction")

            sort += [(field, direction)]
        
        return sort
    '''


'''

# TODO: Create person
# TODO: Delete person
# TODO: Retrieve person
# TODO: List people
# TODO: Update person


class ModelListView(View):

    sort_fields = ['name', 'email']
    filter_fields = ['group']
    search_fields = [] # TODO: implement search engine support

    def get_objects(self, query):
        assert isinstance(query, peewee.Query)

        # apply filters

        # apply pagination
        assert isinstance(self.pagination, QueryPagination)
        query = self.pagination.paginate_query(query)



    def filter_object(self):
        pass


class PersonList(ModelListView):
    query = Person.select()
    pagination = PrimaryKeyPagination()
'''













