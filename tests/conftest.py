import asynctest
import pytest
from unittest import mock
from starlette.applications import Starlette

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


@pytest.yield_fixture(scope='function')
def mw(app, statsd_client):
    yield StatsdMiddleware("default", app, statsd_client)


@pytest.yield_fixture(scope='function')
def send():
    yield asynctest.CoroutineMock()


@pytest.yield_fixture(scope='function')
def receive():
    yield asynctest.CoroutineMock()
