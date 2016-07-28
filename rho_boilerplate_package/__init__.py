__version__ = '0.0.1'
VERSION = tuple(map(int, __version__.split('.')))


# Set default logging handler to avoid "No handler found" warnings.
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:  # pragma: no cover
    class NullHandler(logging.Handler):  # pragma: no cover
        def emit(self, record):  # pragma: no cover
            pass  # pragma: no cover

logging.getLogger(__name__).addHandler(NullHandler())
