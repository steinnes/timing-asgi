from unittest import mock
from starlette.endpoints import HTTPEndpoint
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

    metric_namer = StarletteScopeToName("myapp", starlette_app, fallback=mock.MagicMock())
    assert metric_namer(scope(path="/something")) == "myapp.test_starlette_scope_to_name.something"
    assert metric_namer(scope(path="/something_else")) == "myapp.test_starlette_scope_to_name.something_else"
    assert not metric_namer.fallback.called


def test_starlette_scope_metric_class_based_endpoint(starlette_app, scope):
    @starlette_app.route("/howclassy")
    class HowClassy(HTTPEndpoint):
        def get(self, request):
            return JSONResponse({})

    metric_namer = StarletteScopeToName("myapp", starlette_app, fallback=mock.MagicMock())
    assert metric_namer(scope(path="/howclassy")) == "myapp.test_starlette_scope_to_name.HowClassy"


def test_starlette_scope_metric_uses_name_if_found(starlette_app, scope):
    @starlette_app.route("/fancy", name="this.is.fancy")
    def fancy(request):
        return JSONResponse({})

    metric_namer = StarletteScopeToName("myapp", starlette_app, fallback=mock.MagicMock())
    assert metric_namer(scope(path="/fancy")) == "myapp.test_starlette_scope_to_name.this.is.fancy"


def test_starlette_scope_metric_route_not_found(starlette_app, scope):
    metric_namer = StarletteScopeToName("myapp", starlette_app, fallback=mock.MagicMock())
    assert metric_namer(scope(path="/something")) == metric_namer.fallback.return_value


def test_starlette_scope_metric_fallback_is_path_to_name(starlette_app, scope):
    metric_namer = StarletteScopeToName("myapp", starlette_app)
    assert isinstance(metric_namer.fallback, PathToName)
