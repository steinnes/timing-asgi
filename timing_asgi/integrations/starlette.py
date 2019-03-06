from starlette.routing import Match

from timing_asgi.interfaces import MetricNamer
from timing_asgi.utils import PathToName


class StarletteScopeToName(MetricNamer):
    def __init__(self, prefix, starlette_app, fallback=None):
        self.prefix = prefix
        self.starlette_app = starlette_app
        if fallback is None:
            fallback = PathToName(prefix)
        self.fallback = fallback

    def __call__(self, scope):
        route = None
        for r in self.starlette_app.router.routes:
            if r.matches(scope)[0] == Match.FULL:
                route = r
                break
        if route is not None:
            return f"{self.prefix}.{route.endpoint.__module__}.{route.endpoint.__name__}"
        else:
            return self.fallback(scope)
