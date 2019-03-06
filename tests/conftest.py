import asynctest
import pytest
from unittest import mock
from starlette.applications import Starlette
from starlette.testclient import TestClient

from statsd_asgi import StatsdMiddleware


@pytest.yield_fixture(scope='function')
def starlette_app():
    yield Starlette()


@pytest.yield_fixture(scope='function')
def statsd_client():
    yield mock.MagicMock()


@pytest.yield_fixture(scope='function')
def client(starlette_app):
    yield TestClient(starlette_app)


@pytest.yield_fixture(scope='function')
def mw(starlette_app, statsd_client):
    yield StatsdMiddleware(starlette_app, statsd_client=statsd_client)


@pytest.yield_fixture(scope='function')
def send():
    yield asynctest.CoroutineMock()


@pytest.yield_fixture(scope='function')
def receive():
    yield asynctest.CoroutineMock()


@pytest.fixture
def scope():
    def inner(scope_type=None, method=None, scheme=None, server=None, path=None, headers=None):
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
    return inner
