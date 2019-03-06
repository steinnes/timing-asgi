from unittest import mock

from statsd_asgi.integrations import StarletteScopeMetric
from statsd_asgi.utils import PathScopeMetric


def test_starlette_scope_metric_route_found(starlette_app, scope):
    @starlette_app.route("/something")
    def something():
        return JSONResponse({})

    scope_metric = StarletteScopeMetric("myapp", starlette_app, fallback=mock.MagicMock())
    assert scope_metric(scope(path="/something")) == "myapp.test_starlette_scope_metric.something"
    assert not scope_metric.fallback.called


def test_starlette_scope_metric_route_not_found(starlette_app, scope):
    scope_metric = StarletteScopeMetric("myapp", starlette_app, fallback=mock.MagicMock())
    assert scope_metric(scope(path="/something")) == scope_metric.fallback.return_value


def test_starlette_scope_metric_fallback_is_path_scope_metric(starlette_app, scope):
    scope_metric = StarletteScopeMetric("myapp", starlette_app)
    assert isinstance(scope_metric.fallback, PathScopeMetric)
