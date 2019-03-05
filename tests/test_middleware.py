import pytest

from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from unittest import mock

from statsd_asgi import StatsdMiddleware


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


class FakeTimingStats:
    def __init__(self):
        self.entered = False
    def __enter__(self):
        self.entered = True
    def __enter(self):
        pass


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


def test_statsd_middleware_ensure_compliance_no_timing_attr(app, mw):
    class FakeClient:
        pass

    broken_client = FakeClient()
    with pytest.raises(AssertionError):
        mw.ensure_compliance(broken_client)

def test_statsd_middleware_ensure_compliance_timing_attr_not_callable(app, mw):
    class FakeClient:
        timing = "this is not the method you're looking for"

    broken_client = FakeClient()
    with pytest.raises(AssertionError):
        mw.ensure_compliance(broken_client)


def test_statsd_middleware_ensure_compliance(app, mw):
    class FakeClient:
        def timing(self, *args, **kwargs):
            pass

    working_client = FakeClient()
    assert mw.ensure_compliance(working_client) == working_client


def test_statsd_middleware_init_calls_ensure_compliance(app):
    with mock.patch('statsd_asgi.StatsdMiddleware.ensure_compliance') as mock_ensure_compliance:
        mw = StatsdMiddleware("myapp", app, "foo")
        assert mock_ensure_compliance.called_with("foo")


@pytest.mark.asyncio
async def test_statsd_middleware_asgi_short_circuits_timingstats_if_get_metric_name_raises_exception(mw, send, receive):
    timing_stats = FakeTimingStats()
    setattr(mw, 'get_metric_name', mock.MagicMock(side_effect=AttributeError))
    with mock.patch('statsd_asgi.middleware.alog') as mock_alog:
        with mock.patch('statsd_asgi.middleware.TimingStats', return_value=timing_stats):
            await mw(scope())(receive, send)
    assert not timing_stats.entered
    assert mock_alog.error.called


@pytest.mark.asyncio
async def test_statsd_middleware_asgi_sends_timings(mw, statsd_client, receive, send):
    await mw(scope())(receive, send)
    assert statsd_client.timing.called
