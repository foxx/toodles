from functools import wraps
from json import JSONDecoder, JSONEncoder
from bottle import HTTPResponse, HTTPError, request

from .exceptions import *
from .mediatype import *

__all__ = ['Renderer', 'JSONRenderer', 'Parser', 'OctetStreamParser',
           'JSONParser', 'FormParser', 'ContentNegotiationContext',
           'ContentNegotiationPlugin']


# TODO: Ensure renderer classes only has renderers
# TODO: Auto detect non strings in default renderer and dump
# TODO: Replace html parser with template parser?
# TODO: Detect when non string object has been returned in response (and reject)
# TODO: Add Jinja renderer support
# TODO: Add XML support? urgh
# https://github.com/tiran/defusedxml


############################################################
# Renderers
############################################################

class BaseRenderer(type):
    def __new__(cls, name, bases, attrs):
        obj = super(BaseRenderer, cls).__new__(cls, name, bases, attrs)
        obj.media_types = cast_media_type_list(obj.media_types)
        if not obj.default_media_type:
            obj.default_media_type = obj.media_types[0] \
                if obj.media_types else None
        return obj


class Renderer(with_metaclass(BaseRenderer)):
    media_types = None
    default_media_type = None
    charset = None

    @classmethod
    def render(self, body): # pragma: nocover
        """
        :attr body: Response body
        :type body: bytes
        """
        return body


class JSONRenderer(Renderer):
    media_types = 'application/json'
    encoder = JSONEncoder
    charset = 'utf-8'

    @classmethod
    def render(self, body):
        if body is None:
            return None
        return self.encoder().encode(body).encode(self.charset)


############################################################
# Parsers
############################################################

class BaseParser(type):
    def __new__(cls, name, bases, attrs):
        obj = super(BaseParser, cls).__new__(cls, name, bases, attrs)
        obj.media_types = cast_media_type_list(obj.media_types)
        return obj


class Parser(with_metaclass(BaseParser)):
    media_types = None

    @classmethod
    def parse(self, body): # pragma: nocover
        """
        :attr body: Request body
        :type body: bytes
        """
        return body


class OctetStreamParser(Parser):
    media_types = 'application/octet-stream'
    charset = 'utf-8'

    @classmethod
    def parse(self, body):
        return body


class JSONParser(Parser):
    media_types = 'application/json'
    decoder = JSONDecoder
    charset = 'utf-8'

    @classmethod
    def parse(self, body):
        return self.decoder().decode(body.decode(self.charset)) \
            if body else None


class FormParser(Parser):
    media_types = [
        MediaType('application/x-www-form-urlencoded'), 
        MediaType('multipart/form-data')]

    @classmethod
    def parse(self, body):
        return request.forms


############################################################
# Base objects
############################################################

class ContentNegotiationContext:
    """
    Injected into `bottle.request` on every request which
    has content negotiation enabled
    """

    # Parser instance for request body
    parser = None

    # Renderer instance for response body
    renderer = None

    # Request Content-Type header represented as MediaType instance 
    request_content_type = None

    # Accept headers represented as MediaTypeList instance
    request_accept = None

    # Response Content-Type header represented as MediaType instance
    response_content_type = None

    # Content negotiation instance
    negotiator = None


class ContentNegotiationPlugin:
    """
    Content negotiation plugin 
    """

    parsers = None
    renderers = None
    default_renderer = None

    def guess_content_type(self, body):
        """
        As per RFC7231 section 3.1.1.5, attempt to guess content type
        if one hasn't been provided, and use fallback assumption
        of application/octet-stream.

        TODO: is this correct?

        https://tools.ietf.org/html/rfc7231#section-3.1.1.5

        :returns: MediaType instance
        """
        if body: 
            return MediaType('application/octet-stream')

    def select_parser(self, media_type):
        """
        Determine which parser should be used for request

        :attr media_type: Media type to match
        """
        for parser in self.parsers or []:
            matched = parser.media_types.first_match(media_type)
            if matched: return parser
        return None

    def select_renderer(self, media_type):
        """
        Determine which renderer should be used for response

        :attr media_type: Media type to match
        :returns: (renderer, media_type)
        """
        for renderer in self.renderers or []:
            matched = renderer.media_types.first_match(media_type)
            if matched: 
                return renderer, matched[1]
        return None, None

    def __call__(self, fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                self.process_request()
                resp = fn(*args, **kwargs)
                return self.render_response(resp)
            except Exception as exc:
                self.handle_exception(exc)
                raise
        return wrapper

    def handle_exception(self, exc):

        # Errors should be rendered using content negotiation, where possible
        renderer = None
        if hasattr(request, 'nctx'):
            renderer = self.render_response

        # Any exceptions extending HTTPError should be handled as-is
        # HTTPError should be rendered then re-raised
        if isinstance(exc, HTTPError):
            if renderer: exc.body = renderer(exc.body)
            return
        
        # BaseError should be rendered into new HTTPError
        if isinstance(exc, BaseError):
            nexc = HTTPError(exc.status_code, exc.to_dict(), exception=exc)
            nresp = renderer(nexc)
            raise nresp

    def process_request(self):
        # ensure content negotiation has not already been applied
        if hasattr(request, 'nctx'):
            raise RuntimeError('Content negotiation applied twice on same request')
            
        # assign negotiation context
        request.nctx = nctx = ContentNegotiationContext()
        nctx.negotiator = self

        # determine which content types are accepted by the client
        try:
            raw_accept = request.headers.get('Accept', '*/*')
            nctx.request_accept = MediaTypeList(raw_accept)
        except ParseError as e:
            raise ClientError(
                status_code='400 Invalid Accept',
                error_code='bad_request',
                error_desc="The request header 'Accept' was malformed")

        # determine what content type is sent by the request
        try:
            raw_content_type = request.headers.get('Content-Type', None)
            if raw_content_type:
                nctx.request_content_type = MediaType(raw_content_type)
        except ParseError:
            raise ClientError(
                status_code='400 Invalid Content Type',
                error_code='bad_request',
                error_desc="The request header 'Content-Type' was malformed")

        # looks like content negotiation is enabled on this view
        request.body_parsed = None
        body = request._get_body_string()

        # assign default renderer class
        if self.default_renderer:
            nctx.renderer = self.default_renderer
            nctx.response_content_type = nctx.renderer.default_media_type

        # find appropriate renderer
        if nctx.request_accept:
            nctx.renderer, nctx.response_content_type = \
                self.select_renderer(nctx.request_accept)
            
            # could not negotiate an appropriate renderer
            if (not nctx.renderer and self.renderers \
                and not self.default_renderer):
                raise ClientError(
                    status_code='406 Not Acceptable',
                    error_code='bad_request',
                    error_desc="The server could not negotiate response content based " \
                               "on the 'Accept-*' request headers")

        # attempt to guess content type if necessary
        if body and not raw_content_type:
            nctx.request_content_type = self.guess_content_type(body)

        # find appropriate content parser
        if nctx.request_content_type:
            nctx.parser = self.select_parser(nctx.request_content_type)

            # XXX: needs test
            if not nctx.parser:
                raise ClientError(
                    status_code='415 Unsupported Media Type',
                    error_code='bad_request',
                    error_desc='The specified content type for request body is unsupported')

        # process body
        if nctx.parser:
            try:
                request.body_parsed = nctx.parser.parse(body)
            except Exception as exc:
                #import pdb; pdb.set_trace()
                raise ClientError(
                    status_code='400 Invalid Body',
                    error_code='bad_request',
                    error_desc='There was an error parsing the request body',
                    error_detail=str(exc))

    def render_response(self, resp):
        # always ensure we have a http response instance
        if not isinstance(resp, HTTPResponse):
            resp = HTTPResponse(resp)

        # create new response type
        nresp = HTTPResponse()
        resp.apply(nresp)
        if not request.nctx.renderer: return nresp

        # apply rendering
        nresp.body = request.nctx.renderer.render(nresp.body)
        nresp.content_type = request.nctx.response_content_type
 
        # XXX: manually append charset due to bug
        # https://github.com/bottlepy/bottle/issues/1048
        if request.nctx.renderer.charset:
            to_append = '; charset={}'.format(request.nctx.renderer.charset.upper())
            nresp.content_type += to_append

        return nresp


class ContentNegotiationPlugin:
    """
    Plugin for Content Negotiation
    """

    def setup(self, app):
        # ensure this plugin isn't already installed
        for other in app.plugins:
            if isinstance(other, ContentNegotiationPlugin):
                raise PluginError('ContentNegotiationPlugin already installed')

    def apply(self, callback, context):
        # do we have a renderer?
        return cneg(callback)

