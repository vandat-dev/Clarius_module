from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from service.connection_manager import ConnectionManager

app = FastAPI()
manager = ConnectionManager()

class ConnectRequest(BaseModel):
    device_id: str
    ip: str
    port: int

class DisconnectRequest(BaseModel):
    device_id: str

@app.post("/connect")
def connect_device(req: ConnectRequest):
    success = manager.connect(req.device_id, req.ip, req.port)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to connect or already connected")
    return {"status": "connected", "device_id": req.device_id}

@app.post("/disconnect")
def disconnect_device(req: DisconnectRequest):
    success = manager.disconnect(req.device_id)
    if not success:
        raise HTTPException(status_code=404, detail="Device not found")
    return {"status": "disconnected", "device_id": req.device_id}

@app.get("/connections")
def list_connections():
    return {"connections": manager.list_connections()}
