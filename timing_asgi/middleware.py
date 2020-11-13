import alog

from .utils import PathToName, TimingStats


class TimingMiddleware:
    """Timing middleware for ASGI applications

    Args:
      app (ASGI application): ASGI application
      client (TimingClient): the client used to emit instrumentation metrics
      metric_namer (MetricNamer): the callable used to construct metric names from the ASGI scope
    """

    def __init__(self, app, client, metric_namer=None):
        if metric_namer is None:
            metric_namer = PathToName(prefix="unnamed")

        self.app = app
        self.client = self.ensure_compliance(client)
        self.metric_namer = metric_namer

    def ensure_compliance(self, client):
        assert hasattr(client, "timing")
        assert callable(client.timing)
        return client

    async def __call__(self, scope, receive, send):
        # locals inside the app function (send_wrapper) can't be assigned to,
        # as the interpreter detects the assignment and thus creates a new
        # local variable within that function, with that name.
        instance = {"http_status_code": None}

        def send_wrapper(response):
            if response["type"] == "http.response.start":
                instance["http_status_code"] = response["status"]
            return send(response)

        if scope["type"] != "http":
            alog.debug(f"ASGI scope of type {scope['type']} is not supported yet")
            await self.app(scope, receive, send)
            return

        try:
            metric_name = self.metric_namer(scope)
        except AttributeError as e:
            alog.error(
                f"Unable to extract metric name from asgi scope: {scope}, skipping statsd timing"
            )
            alog.error(f" -> exception: {e}")
            await self.app(scope, receive, send)
            return

        def emit(stats):
            statsd_tags = [
                f"http_status:{instance['http_status_code']}",
                f"http_method:{scope['method']}",
            ]
            self.client.timing(
                f"{metric_name}", stats.time, tags=statsd_tags + ["time:wall"]
            )
            self.client.timing(
                f"{metric_name}", stats.cpu_time, tags=statsd_tags + ["time:cpu"]
            )

        with TimingStats(metric_name) as stats:
            try:
                await self.app(scope, receive, send_wrapper)
            except Exception:
                stats.stop()
                instance["http_status_code"] = 500
                emit(stats)
                raise
        emit(stats)
