import ctypes
import numpy as np
from typing import Any
from initial.data_store import global_caster_data

def newProcessedImage(image: ctypes.c_void_p, width, height, sz, microns, ts, angle, imu: Any):
    try:
        buf = ctypes.string_at(image, sz)
    except Exception as e:
        global_caster_data.message = f"Error reading memory: {e}"
        return

    with global_caster_data.lock:
        global_caster_data.image_bytes = buf
        global_caster_data.image_width = width
        global_caster_data.image_height = height
        global_caster_data.image_size = sz
        global_caster_data.message = "Streaming live data."

def newRawImage(*args):
    pass

def newSpectrumImage(*args):
    pass

def newImuData(*args):
    pass

def freezeFn(frozen: bool):
    with global_caster_data.lock:
        global_caster_data.frozen = frozen
        global_caster_data.message = "Image Frozen." if frozen else "Streaming live data."

def buttonsFn(button: int, clicks: int):
    with global_caster_data.lock:
        global_caster_data.button_info = (button, clicks)
        global_caster_data.message = f"Button {button} pressed ({clicks})."
