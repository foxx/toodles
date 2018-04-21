import pytest
from toodles.web import *
from toodles.web import *
from bottlecap.negotiation import *
from bottlecap.mediatype import *

###########################################################
# Content negotiation
###########################################################

class TestContentNegotiation:
    def test_guess_content_type(self):
        cneg = ContentNegotiation()

        # TODO: is this correct?
        a = cneg.guess_content_type("hello")
        assert a == MediaType('application/octet-stream')

        a = cneg.guess_content_type(None)
        assert a == None

    def test_select_renderer_valid(self):
        class CustomContentNegotiation(ContentNegotiation):
            renderers = [JSONRenderer]

        cneg = CustomContentNegotiation()
        renderer, content_type = cneg.select_renderer('application/json')
        assert renderer == JSONRenderer
        assert content_type == 'application/json'

    def test_select_renderer_blank(self):
        cneg = ContentNegotiation()
        renderer, content_type = cneg.select_renderer('application/json')
        assert renderer == None
        assert content_type == None

    def test_select_parser_valid(self):
        class CustomContentNegotiation(ContentNegotiation):
            parsers = [JSONParser]

        cneg = CustomContentNegotiation()
        parser = cneg.select_parser('application/json')
        assert parser == JSONParser

    def test_select_parser_blank(self):
        cneg = ContentNegotiation()
        parser = cneg.select_parser('application/json')
        assert parser == None

