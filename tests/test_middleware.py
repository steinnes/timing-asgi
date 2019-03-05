import pytest

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from unittest import mock

from statsd_asgi import StatsdMiddleware


@pytest.yield_fixture(scope='function')
def app():
    yield Starlette()


@pytest.yield_fixture(scope='function')
def statsd_client():
    yield mock.MagicMock()


@pytest.yield_fixture(scope='function')
def client(app):
    yield TestClient(app)


def scope(scope_type=None, method=None, scheme=None, server=None, path=None, headers=None):
    if scope_type is None:
        scope_type = "http"
    if method is None:
        method = "GET"
    if scheme is None:
        scheme = "https"
    if server is None:
        server = ("www.example.mock", 80)
    if path is None:
        path = "/"
    if headers is None:
        headers = []

    return {"type": scope_type, "method": method, "scheme": scheme, "server": server, "path": path, "headers": headers}


def test_statsd_middleware_get_metric_name_route_found(app, statsd_client):
    @app.route("/something")
    def something(request):
        return JSONResponse({})
    mw = StatsdMiddleware("myapp", app, statsd_client)
    metric_name = mw.get_metric_name(scope(path="/something"))
    assert metric_name == 'myapp.test_middleware.something'


def test_statsd_middleware_get_metric_name_route_not_found(app, statsd_client):
    mw = StatsdMiddleware("myapp", app, statsd_client)
    metric_name = mw.get_metric_name(scope(path="/something"))
    assert metric_name == 'myapp.something'


def test_statsd_middleware_ensure_compliance():
    pass


def test_statsd_middleware_init_calls_ensure_compliance():
    pass


def test_statsd_middleware_asgi_uses_short_circuits_timingstats_if_no_metric_name():
    pass


def test_statsd_middleware_asgi_sends_timings():
    pass
