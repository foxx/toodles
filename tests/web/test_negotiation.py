import pytest
import json

from toodles.web.content_negotiation import *
from toodles.web.mediatype import *

from werkzeug.wrappers import Request, Response
from werkzeug.test import create_environ


def test_parse_request_accept():
    def test(value):
        headers = Headers()
        headers['Accept'] = value
        environ = create_environ('/foo', 'http://localhost:8080/', headers=headers)
        request = Request(environ)
        return ContentNegotiation.parse_request_accept(request)

    # test single
    value = 'application/json'
    assert test(value) == MediaTypeList(value)

    # test multiple
    value = 'application/json,text/plain;q=0.5'
    assert test(value) == MediaTypeList(value)

    # test invalid
    value = 'lol;q=aa'
    with pytest.raises(ClientError):
        test(value)


def test_parse_request_content_type():
    def test(value):
        headers = Headers()
        headers['Content-Type'] = value
        environ = create_environ('/foo', 'http://localhost:8080/', headers=headers)
        request = Request(environ)

        return ContentNegotiation.parse_request_content_type(request)

    # test with params
    value = 'application/json;q=0.2'
    assert test(value) == MediaType(value)

    # test without params
    value = 'application/json'
    assert test(value) == MediaType(value)

    # test invalid
    value = 'lol;q=aa'
    with pytest.raises(ClientError):
        test(value)


def test_json_request_valid():
    # test data
    tdata = [1,2,3]

    # create request
    headers = Headers()
    headers['Content-Type'] = 'application/json'
    environ = create_environ('/foo', 'http://localhost:8080/',
        headers=headers, data=json.dumps(tdata))
    request = Request(environ)

    # create negotiation
    cneg = ContentNegotiation(
        renderers=[JSONRenderer()],
        parsers=[JSONParser()],
        default_renderer=JSONRenderer())
    cnctx = cneg.create_context(request)

    # does the body get parsed correctly?
    body_parsed = cneg.parse_request_body(request, cnctx)
    assert body_parsed == tdata

    # do we have a correct response?
    resp = Response()
    cneg.render_response(resp, cnctx, [4,5,6])
    assert resp.status_code == 200
    assert resp.get_data() == b'[4, 5, 6]'


def test_json_request_invalid():
    # create request
    headers = Headers()
    headers['Content-Type'] = 'application/json'
    environ = create_environ('/foo', 'http://localhost:8080/',
        headers=headers, data='{22')
    request = Request(environ)

    # create negotiation
    cneg = ContentNegotiation(
        renderers=[JSONRenderer()],
        parsers=[JSONParser()],
        default_renderer=JSONRenderer())
    cnctx = cneg.create_context(request)

    # does the body get parsed correctly?
    with pytest.raises(ClientError) as exc:
        cneg.parse_request_body(request, cnctx)
    assert exc.value.status_code == 400
    assert exc.value.error_detail == \
        'Expecting property name enclosed in double quotes: ' \
        'line 1 column 2 (char 1)'



'''
###########################################################
# Content negotiation
###########################################################

class TestContentNegotiationPlugin:
    def test_guess_content_type(self):
        cneg = ContentNegotiationPlugin()

        # TODO: is this correct?
        a = cneg.guess_content_type("hello")
        assert a == MediaType('application/octet-stream')

        a = cneg.guess_content_type(None)
        assert a == None

    def test_select_renderer_valid(self):
        class CustomContentNegotiationPlugin(ContentNegotiationPlugin):
            renderers = [JSONRenderer]

        cneg = CustomContentNegotiationPlugin()
        renderer, content_type = cneg.select_renderer('application/json')
        assert renderer == JSONRenderer
        assert content_type == 'application/json'

    def test_select_renderer_blank(self):
        cneg = ContentNegotiationPlugin()
        renderer, content_type = cneg.select_renderer('application/json')
        assert renderer == None
        assert content_type == None

    def test_select_parser_valid(self):
        class CustomContentNegotiationPlugin(ContentNegotiationPlugin):
            parsers = [JSONParser]

        cneg = CustomContentNegotiationPlugin()
        parser = cneg.select_parser('application/json')
        assert parser == JSONParser

    def test_select_parser_blank(self):
        cneg = ContentNegotiationPlugin()
        parser = cneg.select_parser('application/json')
        assert parser == None
'''
