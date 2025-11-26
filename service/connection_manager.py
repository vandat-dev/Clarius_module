import threading
import time
import logging
from typing import Dict, Tuple

from initial.client import ClariusCasterClient
from service.frame_sender import GRPCFrameSender

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self, grpc_target: str = "100.86.59.89:50051"):
        self.connections: Dict[str, Tuple[ClariusCasterClient, threading.Thread, threading.Event]] = {}
        self.grpc_sender = GRPCFrameSender(grpc_target)
        self.lock = threading.Lock()

    def connect(self, device_id: str, ip: str, port: int) -> bool:
        with self.lock:
            if device_id in self.connections:
                logger.warning(f"Device {device_id} already connected.")
                return False

            client = ClariusCasterClient()
            if not client.connect(ip, port):
                logger.error(f"Failed to connect to {ip}:{port}")
                return False

            stop_event = threading.Event()
            thread = threading.Thread(target=self._process_frames, args=(client, stop_event, device_id))
            thread.daemon = True
            thread.start()

            self.connections[device_id] = (client, thread, stop_event)
            logger.info(f"Connected to {device_id} ({ip}:{port})")
            return True

    def disconnect(self, device_id: str) -> bool:
        with self.lock:
            if device_id not in self.connections:
                return False

            client, thread, stop_event = self.connections[device_id]
            stop_event.set()
            thread.join(timeout=2.0)
            client.disconnect()
            client.destroy()
            del self.connections[device_id]
            logger.info(f"Disconnected from {device_id}")
            return True

    def _process_frames(self, client: ClariusCasterClient, stop_event: threading.Event, device_id: str):
        logger.info(f"Started frame processing for {device_id}")
        while not stop_event.is_set():
            webp_bytes = client.get_webp_bytes()
            if webp_bytes:
                # TODO: Maybe add device_id to the frame if protocol allows, currently just sending raw bytes
                self.grpc_sender.send_frame(webp_bytes)
            
            time.sleep(0.001)
        logger.info(f"Stopped frame processing for {device_id}")

    def list_connections(self):
        with self.lock:
            return list(self.connections.keys())
