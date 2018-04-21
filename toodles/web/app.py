import inspect
from bottle import Bottle, request
from .content_negotiation import ContentNegotiationPlugin
from .views import View

__all__ = ['Application']


##############################################################################
# BottleCap application
##############################################################################

class Application(Bottle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # disable all existing plugins on bottle to avoid functionality
        # conflicts, such as built-in JSON support. 
        self.plugins = []

        # install content negotiation plugin
        cnp = ContentNegotiationPlugin()
        self.install(cnp)

    def apply(self, callback, context):
        def wrapper(*args, **kwargs):
            # XXX: for some reason, we cannot use extend_instance on request :X
            request.base_url = RequestMixin.base_url
            request.get_full_url = RequestMixin.get_full_url

            # process request
            return callback(*args, **kwargs)
        return wrapper
    
    def route(self, *args, **kwargs):
        """
        Supports both functions and CBVs
        """
        # treat cbv routing differently
        cls = args[0] if len(args) else None
        if inspect.isclass(cls) and issubclass(cls, View):
            return self.routecbv(cls)
        
        # fallback to standard routing
        return super().route(*args, **kwargs)

    def routecbv(self, view:View):
        """
        Same as route(), but for CBVs (class based views)

        :attr view: View class
        """
        # views must provide at least path and method
        assert view._meta.path
        assert view._meta.method

        kwargs = {}
        kwargs['path'] = view._meta.path
        kwargs['method'] = view._meta.method
        kwargs['name'] = view._meta.name
        kwargs['skip'] = view._meta.skip
        kwargs['apply'] = view._meta.plugins
        kwargs['meta'] = view._meta

        cb = view.as_callable()
        self.route(**kwargs)(cb)
        return view


class RequestMixin(object):
    @property
    def base_url(self):
        """
        Return base URL constructed from current request
        """
        url = "{}://{}".format(
            request.urlparts.scheme,
            request.urlparts.hostname)
        port = request.urlparts.port
        # XXX: needs test
        if port and port not in (80, 443):
            url += ":{}".format(port)
        return url

    def get_full_url(self, routename, **kwargs):
        """
        Construct full URL using components from current
        bottle request, merged with get_url()

        For example:
        https://example.com/hello?world=1

        XXX: Needs UT
        """
        url = self.app.get_url(routename, **kwargs)
        return urljoin(self.base_url, url)


