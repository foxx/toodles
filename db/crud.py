import peewee

__all__ = ['Pagination', 'PrimaryKeyPagination', 'CRUD']

####################################################################
# Pagination
####################################################################

class Pagination:
    pass


class CursorPagination(Pagination):
    # TODO: Needs implementation
    pass


class PrimaryKeyPagination(Pagination):
    """
    Primary key pagination
    
    It does not support models with compound keys or no primary key
    as doing so would require using LIMIT/OFFSET which has terrible
    performance at scale. If you want this, send a PR. 
    """

    @classmethod
    def paginate_query(self, query, count, offset=None, sort=None):
        """
        Apply pagination to query

        :attr query: Instance of `peewee.Query`
        :attr count: Max rows to return
        :attr offset: Pagination offset, str/int
        :attr sort: List of tuples, e.g. [('id', 'asc')]

        :returns: Instance of `peewee.Query`
        """
        assert isinstance(query, peewee.Query)
        assert isinstance(count, int)
        assert isinstance(offset, (str, int, type(None)))
        assert isinstance(sort, (list, set, tuple, type(None)))

         # ensure our model has a primary key
        fields = query.model._meta.get_primary_keys()
        if len(fields) == 0:
            raise peewee.ProgrammingError(
                'Cannot apply pagination on model without primary key')

        # ensure our model doesn't use a compound primary key
        if len(fields) > 1:
            raise peewee.ProgrammingError(
                'Cannot apply pagination on model with compound primary key')

        # apply offset
        if offset is not None:
            query = query.where(fields[0] >= offset)

        # do we need to apply sorting?
        order_bys = []
        if sort:
            for field, direction in sort:
                # does this field have a valid sort direction?
                if not isinstance(direction, str):
                    raise ValueError("Invalid sort direction on field '{}'".format(field))

                direction = direction.lower().strip()
                if direction not in ['asc', 'desc']:
                    raise ValueError("Invalid sort direction on field '{}'".format(field))

                # apply sorting
                order_by = peewee.SQL(field)
                order_by = getattr(order_by, direction)()
                order_bys += [order_by]

        # add primary key ordering after user sorting
        order_bys += [fields[0].asc()]

        # apply ordering and limits
        query = query.order_by(*order_bys)
        query = query.limit(count)
        return query


####################################################################
# Model List
# XXX: Restrict which fields can be filtered
# XXX: Add sort capabilities
# XXX: Do we want to add encryption support? (yes but it should be outside here)
####################################################################


class CRUD:
    paginator = None
    query = None

    sort_fields = []
    filter_fields = []

    '''
    def get_sort_schema(self):
        """
        Returns marshmallow schema for validating sort parameters

        This is dynamically generated from `sort_fields` but can be
        overwritten with custom logic if desired
        """
        attrs = {}
        for field in self.sort_fields:
            # convert sort direction to lower and remove any whitespace
            key = 'lower_{}'.format(field)
            attrs[key] = post_load(lambda item: item.lower().strip())

            # validate sort direction
            attrs[field] = marshmallow.fields.String(
                validator=marshmallow.validate.OneOf('asc', 'desc'))

        return type('SortSchema', (marshmallow.Schema,), attrs)

        # do we have valid sort parameters?
        sort_schema = self.get_sort_schema()
        try:
            clean_params = sort_schema.dump(params)
        except marshmallow.ValidationError as exc:
            nexc = ValueError("Invalid sort parameters specified")
            nexc.errors = exc.messages
            raise nexc
    '''


    def get_query(self):
        """Return query for our model"""
        return self.query

    def get_paginator(self):
        """Return pagination for our model"""
        return self.paginator

    def apply_filters(self, query, filters):
        """
        Apply user specified filters to query
        """
        assert isinstance(query, peewee.Query)
        assert isinstance(filters, dict)

    def list(self, filters, cursor, count):
        """
        List items from query
        """
        assert isinstance(filters, dict), "expected filters type 'dict'"
        assert isinstance(cursor, dict), "expected cursor type 'dict'"

        # start with our base query
        query = self.get_query()
        assert isinstance(query, peewee.Query)

        # XXX: convert and apply user specified filters
        #filters = {field.name: cursor[field.name] for field in fields}
        #query.where(

        paginator = self.get_paginator()
        assert isinstance(paginator, Pagination)

        # always include an extra row for next cursor position
        count += 1

        # apply pagination to query
        pquery = paginator.filter_query(query, cursor, count)
        items = [ item for item in pquery ]

        # determine next cursor position
        next_item = items.pop(1)
        next_cursor = next_item.to_pk_ref()

        '''
        # is this field allowed for sort?
        if field not in self.sort_fields:
            raise ValueError("Cannot sort on field '{}'".format(field))
        '''

        return items, next_cursor

    '''
    def retrieve(self, cursor):
        """
        Retrieve items from query
        """
        assert isinstance(cursor, dict), "expected cursor type 'dict'"

        # look for record in query
        query = self.get_query()
        assert isinstance(query, peewee.Query)

        query
        return query.get(**cursor)
    '''
