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
        app = self.app(asgi_scope)
        # locals inside the app function (send_wrapper) can't be assigned to,
        # as the interpreter detects the assignment and thus creates a new
        # local variable within that function, with that name.
        instance = {'http_status_code': None}

        def send_wrapper(response):
            if response['type'] == 'http.response.start':
                instance['http_status_code'] = response['status']
            return send(response)

        if asgi_scope['type'] != 'http':
            alog.info(f"ASGI scope of type {asgi_scope['type']} is not supported yet")
            await app(receive, send)
            return

        try:
            metric_name = self.scope_metric(asgi_scope)
        except AttributeError as e:
            alog.error(f"Unable to extract metric name from asgi scope: {asgi_scope}, skipping statsd timing")
            alog.error(f" -> exception: {e}")
            await app(receive, send)
            return

        with TimingStats(metric_name) as stats:
            await app(receive, send_wrapper)

        statsd_tags = [
            f"http_status:{instance['http_status_code']}",
            f"http_method:{asgi_scope['method']}"
        ]
        self.statsd_client.timing(f"{metric_name}", stats.time, tags=statsd_tags + ["time:wall"])
        self.statsd_client.timing(f"{metric_name}", stats.cpu_time, tags=statsd_tags + ["time:cpu"])
