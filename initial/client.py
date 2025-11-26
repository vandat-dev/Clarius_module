import os
import cv2
import numpy as np
from PIL import Image

from initial.loader import pyclariuscast
from initial.data_store import global_caster_data
from initial.callbacks import (
    newProcessedImage, newRawImage, newSpectrumImage,
    newImuData, freezeFn, buttonsFn
)


class ClariusCasterClient:
    def __init__(self):
        self.caster = None
        self.data_store = global_caster_data

        if pyclariuscast is None:
            self.data_store.message = "Clarius SDK not loaded."
            return

        self.caster = pyclariuscast.Caster(
            newProcessedImage, newRawImage, newSpectrumImage,
            newImuData, freezeFn, buttonsFn
        )

        path = os.path.expanduser("~/")
        if not self.caster.init(path, 640, 480):
            self.data_store.message = "Failed to initialize Caster."
            self.caster = None
        else:
            self.data_store.message = "Caster initialized."

    def connect(self, ip, port, mode="research"):
        if not self.caster:
            return False
        ok = self.caster.connect(ip, port, mode)
        self.data_store.message = "Connected." if ok else "Connect failed..."
        return ok

    def disconnect(self):
        if self.caster:
            self.caster.disconnect()
            self.data_store.message = "Disconnected."

    def get_pil_image(self):
        with self.data_store.lock:
            if not self.data_store.image_bytes:
                return None

            raw = self.data_store.image_bytes
            w = self.data_store.image_width
            h = self.data_store.image_height
            sz = self.data_store.image_size

            bpp = sz / (w * h)

            try:
                if bpp == 4:
                    pil = Image.frombuffer("RGBA", (w, h), raw, "raw", "BGRA", 0, 1)
                    return pil.convert("RGB")
                elif bpp == 1:
                    arr = np.frombuffer(raw, dtype=np.uint8).reshape((h, w))
                    return Image.fromarray(arr, mode='L')
            except Exception as e:
                self.data_store.message = f"Image convert error: {e}"
                return None

        return None

    def get_jpeg_bytes(self):
        with self.data_store.lock:
            if not self.data_store.image_bytes:
                return None

            raw = self.data_store.image_bytes
            w = self.data_store.image_width
            h = self.data_store.image_height
            sz = self.data_store.image_size

            bpp = sz / (w * h)

            try:
                # RAW → numpy
                if bpp == 4:
                    arr = np.frombuffer(raw, dtype=np.uint8).reshape((h, w, 4))
                    arr = arr[..., [2, 1, 0]]  # BGRA → RGB
                elif bpp == 1:
                    arr = np.frombuffer(raw, dtype=np.uint8).reshape((h, w))
                else:
                    return None

                # numpy → JPEG
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 75]
                ok, jpeg = cv2.imencode(".jpg", arr, encode_param)
                if not ok:
                    return None

                return jpeg.tobytes()

            except Exception as e:
                self.data_store.message = f"Image convert error: {e}"
                return None

    def destroy(self):
        if self.caster:
            self.caster.destroy()
            self.caster = None
            self.data_store.message = "Caster destroyed."
