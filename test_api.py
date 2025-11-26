import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print(f"Checking server at {BASE_URL}...")
    try:
        resp = requests.get(f"{BASE_URL}/connections")
        print(f"Initial connections: {resp.json()}")
    except Exception as e:
        print(f"Server not running? Error: {e}")
        return

    # 1. Test Connect (Mock)
    print("\n[1] Testing /connect...")
    payload = {
        "device_id": "test_cam_01",
        "ip": "127.0.0.1", # Mock IP
        "port": 5828
    }
    try:
        resp = requests.post(f"{BASE_URL}/connect", json=payload)
        print(f"Response: {resp.status_code} - {resp.json()}")
    except Exception as e:
        print(f"Connect error: {e}")

    # 2. Check connections list
    print("\n[2] Checking /connections...")
    resp = requests.get(f"{BASE_URL}/connections")
    print(f"Current connections: {resp.json()}")

    # 3. Test Disconnect
    print("\n[3] Testing /disconnect...")
    payload = {"device_id": "test_cam_01"}
    resp = requests.post(f"{BASE_URL}/disconnect", json=payload)
    print(f"Response: {resp.status_code} - {resp.json()}")

    # 4. Final check
    print("\n[4] Final check /connections...")
    resp = requests.get(f"{BASE_URL}/connections")
    print(f"Final connections: {resp.json()}")

if __name__ == "__main__":
    test_api()
