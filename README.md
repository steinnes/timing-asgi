# statsd-asgi
[![CircleCI](https://circleci.com/gh/steinnes/statsd-asgi.svg?style=svg&circle-token=4e141ed4d7231ab6d00dc7b14624d759cf16e1d2)](https://circleci.com/gh/steinnes/statsd-asgi)
[![PyPI Downloads](https://img.shields.io/pypi/dm/statsd-asgi.svg)](https://pypi.org/project/statsd-asgi/)
[![PyPI Version](https://img.shields.io/pypi/v/statsd-asgi.svg)](https://pypi.org/project/statsd-asgi/)
[![License](https://img.shields.io/badge/license-mit-blue.svg)](https://pypi.org/project/statsd-asgi/)

# installation

```
pip install statsd-asgi
```

# usage

Here's an example using the Starlette ASGI framework and Datadog, a popular statsd-based monitoring service.

```python
from statsd_asgi import StatsdMiddleware

from datadog import initialize, statsd

initialize({'api_key': 'datadog api key', 'app_key': 'datadog app key'})

app = Starlette()

@app.route("/")
def homepage(request):
    return PlainTextResponse("hello world")

app.add_middleware(StatsdMiddleware, statsd_client=statsd)
```

