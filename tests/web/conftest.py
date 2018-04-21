import pytest
from webtest import TestApp
from toodles.web import Toodles

@pytest.fixture
def app(request):
    app = Toodles(catchall=True)
    app.webtest = TestApp(app)
    return app
