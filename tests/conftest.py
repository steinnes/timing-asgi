import pytest

from unittest import mock

from starlette.applications import Starlette

from timing_asgi import TimingMiddleware


@pytest.fixture(scope="function")
def starlette_app():
    yield Starlette()


@pytest.fixture(scope="function")
def timing_client(starlette_app):
    yield mock.MagicMock()


@pytest.fixture(scope="function")
def mw(starlette_app, timing_client):
    yield TimingMiddleware(starlette_app, client=timing_client)


@pytest.fixture(scope="function")
def send():
    yield mock.AsyncMock()


@pytest.fixture(scope="function")
def receive():
    yield mock.AsyncMock()


@pytest.fixture
def scope():
    def inner(
        type=None, method=None, scheme=None, server=None, path=None, headers=None
    ):
        if type is None:
            type = "http"
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

        return {
            "type": type,
            "method": method,
            "scheme": scheme,
            "server": server,
            "path": path,
            "headers": headers,
        }

    return inner
