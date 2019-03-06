from timing_asgi.utils import PathToName


def test_timing_middleware_scope_metric_route_not_found(scope, timing_client):
    scope_metric = PathToName(prefix="myapp")
    assert scope_metric(scope(path="/something")) == 'myapp.something'
