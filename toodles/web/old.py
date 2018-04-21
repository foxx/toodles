import code
import click
import json
import inspect
import bottle

from six.moves.urllib.parse import urljoin
from bottle import Bottle, request, HTTPError, HTTPResponse
from decimal import Decimal
from helpful import ensure_subclass, extend_instance
from bottlecap import exceptions as ex
from blinker import signal

from bottlecap.negotiation import ContentNegotiationPlugin
from bottlecap.views import View

# XXX: do we still need this?
    #self.signal_exception = signal('exception')


    # XXX: do we still need this?
    #def handle_exception(self, exc):
    #    """
    #    BottleCap becomes the default handler for all exceptions and
    #    never passes them upstream, effectively eliminating catchall
    #    functionality
    #    """
    #    # All exceptions are passed to subscribers for processing
    #    self.signal_exception.send(exc)
        # All other exceptions should be converted into HTTPError
        #if request.app.catchall is True:
        #    nexc = ex.ServerError()
        #    raise HTTPError(nexc.status_code, nexc.to_dict())



'''
class ViewMeta(type):
    """Adds support for class meta"""

    @property
    def _meta(cls):
        o = {}
        for scls in reversed(cls.__mro__):
            meta = getattr(scls, 'Meta', None)
            if not meta: continue
            fields = dict([ (f, getattr(meta, f)) for f in dir(scls.Meta) 
                       if not f.startswith('_') ])
            o.update(fields)

        # TODO: ensure meta has path and method defined
        return ClassDict(o)
'''


ContentNegotiation(
    default_parsers = [],
    default_renderers = [])

class ListItemContentNegotiation(ContentNegotiation):
    """Custom content negotiation for ListItem"""
    parsers = None
    renderers = None


class CustomContentNegotiation:
    parsers = []
    renderers = []
    default_renderer = None


class CustomToodles(Toodles):
    content_negotiation = CustomContentNegotiation


class ListItem:
    parsers = []
    renderers = []
    request_query_schema = None
    request_body_schema = None
    response_body_schema = None



