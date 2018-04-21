"""."""
from urllib.parse import parse_qsl

from toodles.parse.query_namespaces import namespaces


class QueryStringParser(object):
    """Request query string object."""

    def __init__(self, ns_module=''):
        """Initialization method.

        Load available namespaces.
        """
        self.supported_ns = {ns.name: ns for ns in namespaces}

    def parse(self, query_string, max_query_key_tokens=1):
        """."""
        try:
            # Completely disable errors suppressing
            # We want the query string to be valid 100%
            query_parts = parse_qsl(
                query_string,
                strict_parsing=True,
                keep_blank_values=True
            )
        except ValueError as e:
            # TODO: toodles specific exception class
            raise Exception('Malformed query string: %s' % e)

        # For each query attempt to find a matching namespace class
        parsed = []
        for query in query_parts:
            try:
                ns = self.supported_ns[query[0].split('.', 1)[0]]
            except KeyError:
                errmsg = "No query namespace available for '%s' query"
                errmsg %= ''.join(query)
                # TODO: toodles specific exception class
                raise Exception(errmsg)

            # There exists such namespace so parse a query
            parsed.append(ns(max_key_tokens=max_query_key_tokens).parse(query))

        return parsed
