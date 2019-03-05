# statsd-asgi

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

