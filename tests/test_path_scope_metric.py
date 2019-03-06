from statsd_asgi.utils import PathScopeMetric


def test_statsd_middleware_scope_metric_route_not_found(scope, statsd_client):
    scope_metric = PathScopeMetric(prefix="myapp")
    assert scope_metric(scope(path="/something")) == 'myapp.something'
