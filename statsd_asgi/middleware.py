import alog
import functools

from .utils import PathScopeMetric, TimingStats


class StatsdMiddleware:
    def __init__(self, app, statsd_client, scope_metric=None):
        if scope_metric is None:
            scope_metric = PathScopeMetric(prefix="unnamed")

        self.app = app
        self.statsd_client = self.ensure_compliance(statsd_client)
        self.scope_metric = scope_metric

    def ensure_compliance(self, statsd_client):
        assert hasattr(statsd_client, 'timing')
        assert callable(statsd_client.timing)
        return statsd_client

    def __call__(self, scope):
        return functools.partial(self.asgi, asgi_scope=scope)

    async def asgi(self, receive, send, asgi_scope):
        inner = self.app(asgi_scope)

        try:
            metric_name = self.scope_metric(asgi_scope)
        except AttributeError as e:
            alog.error(f"Unable to extract metric name from asgi scope: {asgi_scope}, skipping statsd timing")
            await inner(receive, send)
            return

        def send_wrapper(*args, **kwargs):
            print("send_wrapper(", args, ", ", kwargs, ")")
            return send(*args, **kwargs)

        with TimingStats(metric_name) as stats:
            print("woooo")
            await inner(receive, send_wrapper)
        # XXX: tags [githash is a must at least]
        # XXX: http response status code? (makes no sense for websockets)
        # XXX: sample rate?
        self.statsd_client.timing(f"{metric_name}", stats.time)
        self.statsd_client.timing(f"{metric_name}.cpu", stats.cpu_time)
