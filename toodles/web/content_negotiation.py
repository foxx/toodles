import pytest

from typing import List
from json import JSONDecoder, JSONEncoder, JSONDecodeError

from werkzeug.wrappers import Request, Response
from werkzeug.datastructures import Headers

from .mediatype import MediaType, MediaTypeList
from .exceptions import ClientError, BadRequestError

###############################################################################
# Renderers
###############################################################################

class Renderer:
    # TODO: need some sort of class validation (ensuring vars are correct)
    media_types = None
    default_media_type = None
    charset = None

    @classmethod
    def render(self, body): # pragma: nocover
        raise NotImplementedError()


class JSONRenderer(Renderer):
    media_types = 'application/json'
    encoder = JSONEncoder()
    charset = 'utf-8'

    @classmethod
    def render(self, body):
        if body is None: return None
        return self.encoder.encode(body).encode(self.charset)


###############################################################################
# Parsers
###############################################################################

class Parser:
    media_types = None

    @classmethod
    def parse(self, request): # pragma: nocover
        raise NotImplementedError()


class FormParser(Parser):
    media_types = [
        'application/x-www-form-urlencoded',
        'multipart/form-data']

    @classmethod
    def parse(self, request):
        return request.form


class JSONParser(Parser):
    media_types = ['application/json']
    decoder = JSONDecoder()
    charset = 'utf-8'

    @classmethod
    def parse(self, request):
        if not request.data: 
            return None

        try:
            return self.decoder.decode(
                request.data.decode(self.charset))
        except JSONDecodeError as exc:
            raise BadRequestError(
                error_desc='Failed to parse request body',
                error_detail=str(exc))


class FileUploadParser(Parser):
    media_types = ['application/json']

    @classmethod
    def parse(self, request):
        return request.files


###############################################################################
# Content negotiator
###############################################################################

class ContentNegotiationContext:
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


class ContentNegotiation:
    renderers = None
    parsers = None
    default_renderer = None

    def __init__(self, renderers:List[Renderer], parsers:List[Parser], 
                 default_renderer=None):
        self.renderers = renderers
        self.parsers = parsers
        self.default_renderer = default_renderer

    def parse_request_body(self, request:Request, ctx:ContentNegotiationContext):
        """
        Returns parsed request body object or raises error
        """
        if not ctx.parser: return None
        try:
            return ctx.parser.parse(request)
        except Exception as exc:
            raise
            # TODO: need to re-raise user friendly errors from parsers, as we
            # shouldn't throw unsanitised exception messages to the user
            raise ClientError(
                status_code='400 Invalid Body',
                error_code='bad_request',
                error_desc='There was an error parsing the request body')

    def render_response(self, response:Response, ctx:ContentNegotiationContext, body):
        """
        Apply content negotiation rendering to an existing response
        """
        # only set content-type if not already
        if not response.content_type:
            response.content_type = ctx.response_content_type
            if ctx.renderer.charset:
                x = '; charset={}'.format(ctx.renderer.charset.upper())
                response.content_type += x

        # render body
        rendered_body = ctx.renderer.render(body)
        response.set_data(rendered_body)

    def select_renderer(self, media_type):
        """
        Find best matching renderer for given media type

        :attr media_type: Media type to match
        :returns: (renderer, media_type)
        """
        for renderer in self.renderers or []:
            matched = MediaTypeList(renderer.media_types).first_match(media_type)
            if matched: 
                return renderer, matched[1]
        return None, None

    def select_parser(self, media_type):
        """
        Find matching parser for given media type

        :attr media_type: Media type to match
        """
        for parser in self.parsers or []:
            matched = MediaTypeList(parser.media_types).first_match(media_type)
            if matched: return parser
        return None

    def create_context(self, request:Request):
        """
        Returns content negotiation context for request
        """

        cnctx = ContentNegotiationContext()
        cnctx.negotiator = self
        cnctx.request_accept = self.parse_request_accept(request)
        cnctx.request_content_type = self.parse_request_content_type(request)

        # As per RFC7231 section 3.1.1.5, use default if none provided
        # https://tools.ietf.org/html/rfc7231#section-3.1.1.5
        if not cnctx.request_content_type:
            cnctx.request_content_type = MediaType('application/octet-stream')

        # do we have a parser?
        if cnctx.request_content_type:
            cnctx.parser = self.select_parser(cnctx.request_content_type)

        # content type was provided by client but no matching parser found
        if cnctx.request_content_type and not cnctx.parser:
            raise ClientError(
                status_code='415 Unsupported Media Type',
                error_code='bad_request',
                error_desc="Unsupported content type, cannot parse request body")

        # do we have a default renderer?
        if self.default_renderer:
            cnctx.renderer = self.default_renderer
            cnctx.response_content_type = cnctx.renderer.default_media_type

        # do we have a valid accept header?
        if cnctx.request_accept:
            cnctx.renderer, cnctx.response_content_type = \
                self.select_renderer(cnctx.request_accept)

        # do we have a renderer?
        if not cnctx.renderer:
            raise ClientError(
                status_code='406 Not Acceptable',
                error_code='bad_request',
                error_desc="Content negotiation failed, check your 'Accept' " \
                           "request header and try again")

        return cnctx

    @classmethod
    def parse_request_accept(self, request:Request):
        """
        Parse 'Accept' header from request

        :returns: Instance of MediaTypeList
        """
        try:
            value = request.headers.get('Accept')
            return MediaTypeList(value)
        except ValueError:
            raise ClientError(
                status_code='400 Invalid Accept',
                error_code='bad_request',
                error_desc='The request header \'Accept\' was malformed')

    @classmethod
    def parse_request_content_type(self, request:Request):
        """
        Parse 'Content-Type' header from request

        :returns: Instance of MediaType
        """
        try:
            value = request.headers.get('Content-Type')
            return MediaType(value)
        except ValueError:
            raise ClientError(
                status_code='400 Invalid Content Type',
                error_code='bad_request',
                error_desc='The request header \'Content-Type\' was malformed')



###############################################################################


