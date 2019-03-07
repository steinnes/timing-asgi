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
import uvicorn

from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from timing_asgi import TimingMiddleware, TimingClient
from timing_asgi.integrations import StarletteScopeToName


class PrintTimings(TimingClient):
    def timing(self, metric_name, timing, tags):
        print(metric_name, timing, tags)


app = Starlette()


@app.route("/")
def homepage(request):
    return PlainTextResponse("hello world")


app.add_middleware(
    TimingMiddleware,
    client=PrintTimings(),
    metric_namer=StarletteScopeToName(prefix="myapp", starlette_app=app)
)

if __name__ == "__main__":
    uvicorn.run(app)

```

Running this example and sending some requests:

```
$ python app.py
INFO: Started server process [35895]
INFO: Waiting for application startup.
2019-03-07 11:38:01 INFO  [timing_asgi.middleware:44] ASGI scope of type lifespan is not supported yet
INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO: ('127.0.0.1', 58668) - "GET / HTTP/1.1" 200
myapp.__main__.homepage 0.0006690025329589844 ['http_status:200', 'http_method:GET', 'time:wall']
myapp.__main__.homepage 0.0006950000000000012 ['http_status:200', 'http_method:GET', 'time:cpu']
INFO: ('127.0.0.1', 58684) - "GET /asdf HTTP/1.1" 404
myapp.asdf 0.0005478858947753906 ['http_status:404', 'http_method:GET', 'time:wall']
myapp.asdf 0.0005909999999999804 ['http_status:404', 'http_method:GET', 'time:cpu']
```

A more realistic example which emits the timing metrics to Datadog can be found
[here](https://github.com/steinnes/timing-starlette-asgi-example).
