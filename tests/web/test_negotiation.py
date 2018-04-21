import pytest
from toodles.web.content_negotiation import *
from toodles.web.mediatype import *

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

