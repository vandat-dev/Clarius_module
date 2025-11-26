import threading
from typing import Optional, Tuple

class CasterData:
    def __init__(self):
        self.image_bytes: Optional[bytes] = None
        self.image_width: int = 0
        self.image_height: int = 0
        self.image_size: int = 0
        self.frozen: bool = False
        self.button_info: Optional[Tuple[int, int]] = None
        self.message: str = "Initialized. Ready to connect."
        self.lock = threading.Lock()

# Global shared state
# global_caster_data = CasterData()  # Removed: Now using instance-based CasterData
