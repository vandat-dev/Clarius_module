# import numpy as np
from initial.client import ClariusCasterClient
from service.frame_sender import GRPCFrameSender

client = ClariusCasterClient()
sender = GRPCFrameSender("100.86.59.89:50051")

if client.connect("10.3.5.96", 5828):
    print("Connected. Waiting frame...")

    import time
    start = time.time()

    while True:
        webp_bytes = client.get_webp_bytes()
        if webp_bytes:
            print("sending frame...")
            sender.send_frame(webp_bytes)
        time.sleep(0.001)

client.destroy()