"""."""
from toodles.parse.query_modifiers import *

__all__ = ['SortNameSpace', 'FilterNameSpace']


# FIXME: ban from instantiating this class
class QueryNameSpace(object):
    """Base query namespace class."""

    name = ''
    key_separator = '.'
    mod_separator = ':'

    def __init__(self, max_key_tokens=1):
        """Initialization method."""
        self.max_key_tokens = max_key_tokens

    def parse_key(self, key_str):
        """Parse namespace key."""
        tokens = key_str.split(self.key_separator)[1:]

        tokens_num = len(tokens)
        if self.max_key_tokens < tokens_num:
            errmsg = 'Namespace key is too long: %i (max allowed %i)'
            errmsg %= (tokens_num, self.max_key_tokens)
            raise Exception(errmsg)

        return tokens

    def parse_value(self, value_str):
        """Parse namespace value."""
        pass
        # FIXME: get right modifier class without iteration
        #        (approach as in query_string_parser.py doesn't work)


class FilterNameSpace(QueryNameSpace):
    """."""

    name = 'filter'
    key_separator = '.'
    mod_separator = ':'
    modifiers = [
        BetweenModifier,
        GreaterThenModifier,
        GreaterOrEqualModifier,
        LessThenModifier,
        LessOrEqualModifier,
        InModifier,
        ExactModifier,
        ContainsModifier
    ]

    # NOTE: can be moved to a parent class depending on whether other
    #       namespaces can be fit into the same framework
    def parse(self, query):
        """."""
        return (self.parse_key(query[0]), self.parse_value(query[1]))


class SortNameSpace(QueryNameSpace):
    """."""

    name = 'sort'
