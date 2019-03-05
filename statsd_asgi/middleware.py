import alog
import functools

from .utils import TimingStats


class StatsdMiddleware:
    def __init__(self, name, app, statsd_client):
        self.name = name
        self.app = app
        self.statsd_client = self.ensure_compliance(statsd_client)

    def ensure_compliance(self, statsd_client):
        assert hasattr(statsd_client, 'timing')
        assert callable(statsd_client.timing)
        return statsd_client

    def __call__(self, scope):
        return functools.partial(self.asgi, asgi_scope=scope)

    def get_metric_name(self, scope):
        route = None
        for r in self.app.routes:
            if r.matches(scope):
                route = r
                break
        if route is not None:
            return f"{self.name}.{route.endpoint.__module__}.{route.endpoint.__name__}"
        else:
            path = scope.get('path')[1:]
            return f"{self.name}.{path.replace('/', '.')}"

    async def asgi(self, receive, send, asgi_scope):
        inner = self.app(asgi_scope)

        try:
            metric_name = self.get_metric_name(asgi_scope)
        except AttributeError:
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
