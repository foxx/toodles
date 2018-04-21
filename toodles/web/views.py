from bottlecap.negotiation import ContentNegotiation
from helpful import ClassDict

__all__ = ['View']


############################################################
# CBVs (class based views)
############################################################

class BaseView:
    pass


class ContentNegotiationViewMixin:
    # Choose from these parsers, if no matching content type
    # can be found then return "415 Unsupported Media Type"
    parsers = None

    # Choose from these renderers, if no matching content type
    # can be found then return the first by default
    # See http://tools.ietf.org/html/rfc7231#section-5.3.2
    renderers = None

    # If client provides an Accept header which is not present in
    # our list of renderers, then use this one by default. Otherwise
    # return "406 Not Acceptable"
    # See http://tools.ietf.org/html/rfc7231#section-5.3.2
    default_renderer = None


class View(BaseView, ContentNegotiationViewMixin):
    name = None
    method = None
    path = None
    skip = None
    plugins = None
    config = None

    def __init__(self, **url_args):
        self.url_args = url_args

    def __call__(self):
        return self.dispatch()

    def dispatch(self): # pragma: nocover
        # XXX: should replace with ABCs
        raise NotImplementedError("Subclass must implement dispatch")

    @classmethod
    def as_callable(cls):
        def inner(**url_args):
            return cls(**url_args)()
        return inner

