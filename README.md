# timing-asgi
[![CircleCI](https://circleci.com/gh/steinnes/timing-asgi.svg?style=svg&circle-token=4e141ed4d7231ab6d00dc7b14624d759cf16e1d2)](https://circleci.com/gh/steinnes/timing-asgi)
[![PyPI Downloads](https://img.shields.io/pypi/dm/timing-asgi.svg)](https://pypi.org/project/timing-asgi/)
[![PyPI Version](https://img.shields.io/pypi/v/timing-asgi.svg)](https://pypi.org/project/timing-asgi/)
[![License](https://img.shields.io/badge/license-mit-blue.svg)](https://pypi.org/project/timing-asgi/)

This is a timing middleware for ASGI, useful for automatic instrumentation of ASGI endpoints.

This was developed at [GRID](https://github.com/GRID-is) for use with our backend services which are built using
python and the ASGI framework [Starlette](https://starlette.io), and intended to emit metrics to [Datadog](https://datadog.com),
a statsd-based cloud monitoring service.

# installation

```
pip install timing-asgi
```

# usage

Here's an example using the Starlette ASGI framework and Datadog, a popular statsd-based monitoring service.

```python
import os
import uvicorn

from datadog import initialize, statsd
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from timing_asgi import TimingMiddleware, TimingClient
from timing_asgi.integrations import StarletteScopeToName


initialize({'api_key': 'datadog api key', 'app_key': 'datadog app key'})

app = Starlette()


class StatsdClient(TimingClient):
    def __init__(self, datadog_client, tags=None):
        if tags is None:
            tags = []
        self.tags = tags
        self.datadog_client = datadog_client

    def timing(self, metric_name, timing, tags):
        self.datadog_client.timing(metric_name, timing, tags + self.tags)


@app.route("/")
def homepage(request):
    return PlainTextResponse("hello world")

app.add_middleware(
    TimingMiddleware,
    client=StatsdClient(
        datadog_client=statsd,
        tags=['app_version:'.format(os.environ.get('GITHASH'), 'unknown')],
    ),
    metric_namer=StarletteScopeToName(
        prefix="myapp",
        starlette_app=app
    )
)

if __name__ == "__main__":
    uvicorn.run(app)
```

This is example can also be found [here](https://github.com/steinnes/timing-starlette-asgi-example).
