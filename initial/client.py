import os
import cv2
import numpy as np
import ctypes
from typing import Any
from PIL import Image

from initial.loader import pyclariuscast
from initial.data_store import CasterData


class ClariusCasterClient:
    def __init__(self):
        self.caster = None
        self.data_store = CasterData()

        print(f"[DEBUG ClariusCasterClient.__init__] pyclariuscast module = {pyclariuscast}")
        
        if pyclariuscast is None:
            self.data_store.message = "Clarius SDK not loaded."
            print("[DEBUG] ❌ Clarius SDK not loaded! pyclariuscast is None")
            return

        # Define callbacks as closures to capture self.data_store
        def newProcessedImage(image: ctypes.c_void_p, width, height, sz, microns, ts, angle, imu: Any):
            try:
                buf = ctypes.string_at(image, sz)
            except Exception as e:
                self.data_store.message = f"Error reading memory: {e}"
                return

            with self.data_store.lock:
                self.data_store.image_bytes = buf
                self.data_store.image_width = width
                self.data_store.image_height = height
                self.data_store.image_size = sz
                self.data_store.message = "Streaming live data."

        # Unused callbacks (required by Caster signature)
        newRawImage = lambda *args: None
        newSpectrumImage = lambda *args: None
        newImuData = lambda *args: None

        def freezeFn(frozen: bool):
            with self.data_store.lock:
                self.data_store.frozen = frozen
                self.data_store.message = "Image Frozen." if frozen else "Streaming live data."

        def buttonsFn(button: int, clicks: int):
            with self.data_store.lock:
                self.data_store.button_info = (button, clicks)
                self.data_store.message = f"Button {button} pressed ({clicks})."

        # Keep references to callbacks to prevent garbage collection
        self._callbacks = (newProcessedImage, newRawImage, newSpectrumImage, newImuData, freezeFn, buttonsFn)

        self.caster = pyclariuscast.Caster(
            newProcessedImage, newRawImage, newSpectrumImage,
            newImuData, freezeFn, buttonsFn
        )
        print(f"[DEBUG] ✓ Caster object created: {self.caster}")

        path = os.path.expanduser("~/")
        print(f"[DEBUG] Calling caster.init(path='{path}', width=640, height=480)")
        init_result = self.caster.init(path, 640, 480)
        print(f"[DEBUG] caster.init() returned: {init_result}")
        
        if not init_result:
            self.data_store.message = "Failed to initialize Caster."
            print("[DEBUG] ❌ caster.init() FAILED! Setting self.caster = None")
            self.caster = None
        else:
            self.data_store.message = "Caster initialized."
            print("[DEBUG] ✓ Caster initialized successfully!")

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

    def get_webp_bytes(self):
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

                # numpy → WEBP
                encode_param = [int(cv2.IMWRITE_WEBP_QUALITY), 75]
                ok, webp = cv2.imencode(".webp", arr, encode_param)
                if not ok:
                    return None

                return webp.tobytes()

            except Exception as e:
                self.data_store.message = f"Image convert error: {e}"
                return None

    def destroy(self):
        if self.caster:
            self.caster.destroy()
            self.caster = None
            self.data_store.message = "Caster destroyed."
