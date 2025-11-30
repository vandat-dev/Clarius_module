import logging
import grpc

from frame_pb2 import FrameRequest
from frame_pb2_grpc import FrameServiceStub


logger = logging.getLogger(__name__)

class GRPCFrameSender:
    def __init__(self, target: str):
        self.target = target
        self.channel = grpc.insecure_channel(self.target)
        self.stub = FrameServiceStub(self.channel)

    async def send_frame(self, frames: list[bytes]) -> dict:
        """Gửi nhiều JPEG frames liên tục, không chờ response từng cái."""

        async def request_generator():
            for f in frames:
                if not f:
                    continue
                yield FrameRequest(data=f)
            # Khi yield xong => đóng stream

        try:
            # Chỉ nhận response 1 lần cuối
            await self.stub.SendFrame(request_generator())
            return {"ok": True, "message": f"Sent {len(frames)} frames"}

        except Exception as e:
            logger.error(f"Lỗi gRPC streaming: {e}")
            return {"ok": False, "message": str(e)}

    # def send_frame(self, jpeg_bytes: bytes) -> dict:
    #     """Send 1 JPEG frame over gRPC (not using numpy RAW)"""
    #     if not jpeg_bytes:
    #         raise ValueError("Frame trống, không thể gửi.")
    #
    #     try:
    #         # Send frame JPEG
    #         self.stub.SendFrame(FrameRequest(data=jpeg_bytes))
    #         return {"ok": True, "message": "Frame sent"}
    #
    #     except Exception as e:
    #         logger.error(f"Lỗi gửi frame: {e}")
    #         return {"ok": False, "message": str(e)}