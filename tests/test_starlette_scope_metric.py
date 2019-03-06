from unittest import mock
from starlette.responses import JSONResponse

from timing_asgi.integrations import StarletteScopeToName
from timing_asgi.utils import PathToName


def test_starlette_scope_metric_route_found(starlette_app, scope):
    @starlette_app.route("/something")
    def something():
        return JSONResponse({})

    @starlette_app.route("/something_else")
    def something_else():
        return JSONResponse({})

    scope_metric = StarletteScopeToName("myapp", starlette_app, fallback=mock.MagicMock())
    assert scope_metric(scope(path="/something")) == "myapp.test_starlette_scope_metric.something"
    assert scope_metric(scope(path="/something_else")) == "myapp.test_starlette_scope_metric.something_else"
    assert not scope_metric.fallback.called


def test_starlette_scope_metric_route_not_found(starlette_app, scope):
    scope_metric = StarletteScopeToName("myapp", starlette_app, fallback=mock.MagicMock())
    assert scope_metric(scope(path="/something")) == scope_metric.fallback.return_value


def test_starlette_scope_metric_fallback_is_path_scope_metric(starlette_app, scope):
    scope_metric = StarletteScopeToName("myapp", starlette_app)
    assert isinstance(scope_metric.fallback, PathToName)
