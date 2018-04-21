import pytest
from webtest import TestApp
from toodles import Toodles

@pytest.fixture
def app(request):
    tapp = Toodles()
    tapp.wsgiapp.test = TestApp(tapp.wsgiapp)
    return app
