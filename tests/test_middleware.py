import pytest

from unittest import mock

from statsd_asgi import StatsdMiddleware



class FakeTimingStats:
    def __init__(self):
        self.entered = False

    def __enter__(self):
        self.entered = True

    def __enter(self):
        pass


def test_statsd_middleware_ensure_compliance_no_timing_attr(starlette_app, mw):
    class FakeClient:
        pass

    broken_client = FakeClient()
    with pytest.raises(AssertionError):
        mw.ensure_compliance(broken_client)


def test_statsd_middleware_ensure_compliance_timing_attr_not_callable(starlette_app, mw):
    class FakeClient:
        timing = "this is not the method you're looking for"

    broken_client = FakeClient()
    with pytest.raises(AssertionError):
        mw.ensure_compliance(broken_client)


def test_statsd_middleware_ensure_compliance(starlette_app, mw):
    class FakeClient:
        def timing(self, *args, **kwargs):
            pass

    working_client = FakeClient()
    assert mw.ensure_compliance(working_client) == working_client


def test_statsd_middleware_init_calls_ensure_compliance(starlette_app):
    with mock.patch('statsd_asgi.StatsdMiddleware.ensure_compliance') as mock_ensure_compliance:
        StatsdMiddleware(starlette_app, statsd_client="foo")
    assert mock_ensure_compliance.called_with("foo")


@pytest.mark.asyncio
async def test_statsd_middleware_asgi_skips_timingstats_if_scope_metric_raises_exception(mw, scope, send, receive):
    mw.scope_metric = mock.MagicMock(side_effect=AttributeError)
    timing_stats = FakeTimingStats()
    with mock.patch('statsd_asgi.middleware.alog') as mock_alog:
        with mock.patch('statsd_asgi.middleware.TimingStats', return_value=timing_stats):
            await mw(scope())(receive, send)
    assert not timing_stats.entered
    assert mock_alog.error.called


@pytest.mark.asyncio
async def test_statsd_middleware_asgi_skips_timingstats_if_scope_type_is_not_http(mw, scope, send, receive):
    timing_stats = FakeTimingStats()
    with mock.patch('statsd_asgi.middleware.alog') as mock_alog:
        with mock.patch('statsd_asgi.middleware.TimingStats', return_value=timing_stats):
            await mw(scope(type='websocket'))(receive, send)
    assert not timing_stats.entered
    assert mock_alog.info.called


@pytest.mark.asyncio
async def test_statsd_middleware_asgi_sends_timings(mw, scope, statsd_client, receive, send):
    await mw(scope())(receive, send)
    assert statsd_client.timing.called
