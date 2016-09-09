"""
Compatibility layer and utilities.
"""
import base64
import sys

PY3 = sys.version_info[0] >= 3

# Python 3 does not have StringIO, we should use the io module instead
try:
    from StringIO import StringIO  # noqa
except ImportError:
    from io import StringIO  # noqa


def b64encode(bytes_or_str):
    input_bytes = bytes_or_str
    if PY3 and isinstance(bytes_or_str, str):
        input_bytes = bytes_or_str.encode('ascii')

    output_bytes = base64.b64encode(input_bytes)
    if PY3:
        return output_bytes.decode('ascii')
    return output_bytes
