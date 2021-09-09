import platform
import time
import warnings

try:
    import resource
except ModuleNotFoundError as exception:
    if platform.system() == "Windows":
        warnings.warn("resource module not available for Windows, cpu time will be set to 0")
    else:
        raise exception

from .interfaces import MetricNamer


def get_cpu_time():
    if platform.system() == "Windows":
        return 0

    resources = resource.getrusage(resource.RUSAGE_SELF)
    # add up user time (ru_utime) and system time (ru_stime)
    return resources[0] + resources[1]


class TimingStats(object):
    def __init__(self, name=None):
        self.name = name

    def start(self):
        self.start_time = time.time()
        self.start_cpu_time = get_cpu_time()

    def stop(self):
        self.end_time = time.time()
        self.end_cpu_time = get_cpu_time()

    def __enter__(self):
        self.start()
        return self

    @property
    def time(self):
        return self.end_time - self.start_time

    @property
    def cpu_time(self):
        return self.end_cpu_time - self.start_cpu_time

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()


class PathToName(MetricNamer):
    def __init__(self, prefix):
        self.prefix = prefix

    def __call__(self, scope):
        path = scope.get("path")[1:]
        return f"{self.prefix}.{path.replace('/', '.')}"
