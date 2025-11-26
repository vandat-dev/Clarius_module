import ctypes
import sys

pyclariuscast = None
libcast_handle = None

try:
    if sys.platform.startswith("linux"):
        libcast_handle = ctypes.CDLL("initial/libcast.so", ctypes.RTLD_GLOBAL)._handle
        from initial import pyclariuscast
    else:
        from initial import pyclariuscast
except Exception as e:
    print(f"Failed to load Clarius SDK: {e}")
    pyclariuscast = None
