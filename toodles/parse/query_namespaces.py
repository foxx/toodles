"""."""


# FIXME: ban from instantiating this class
class QueryNameSpace(object):
    """Base query namespace class."""

    name = ''
    key_separator = '.'
    mod_separator = ':'

    def parse_key(self, key_str):
        """Parse namespace key."""
        tokens = key_str.split(self.key_separator)[1:]

        tokens_num = len(tokens)
        if self.max_key_tokens < tokens_num:
            errmsg = 'Namespace key is too long: %i (max allowed %i)'
            errmsg %= (tokens_num, self.max_key_tokens)
            raise Exception(errmsg)

        return tokens


class FilterNameSpace(QueryNameSpace):
    """."""

    name = 'filter'
    key_separator = '.'
    mod_separator = ':'

    def __init__(self, max_key_tokens=1):
        """Initialization method."""
        self.max_key_tokens = max_key_tokens

    def parse(self, query):
        """."""
        parsed = []
        parsed.append(self.parse_key(query[0]))
        # TODO: parse value


class SortNameSpace(QueryNameSpace):
    """."""

    name = 'sort'


namespaces = [SortNameSpace, FilterNameSpace]
