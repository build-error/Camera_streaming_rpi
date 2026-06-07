import socket
import struct
import cv2
import numpy as np
import subprocess
import time

PI_IP = "192.168.10.2"
PI_USER = "hanggu-pi5"
PI_STREAM_SCRIPT = "~/Drone/Camera_streaming_rpi/stream.py"
PORT = 9999

# --------------------------------------------------
# Wait for Raspberry Pi to become reachable
# --------------------------------------------------

print("Waiting for Raspberry Pi...")

while True:

    result = subprocess.run(
        [
            "ping",
            "-c",
            "1",
            "-W",
            "1",
            PI_IP
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    if result.returncode == 0:
        print(f"Raspberry Pi reachable ({PI_IP})")
        break

    print("Pi not reachable. Retrying in 5 seconds...")
    time.sleep(5)

# --------------------------------------------------
# Kill old stream server
# --------------------------------------------------

print("Stopping old stream server...")

try:

    subprocess.run(
        [
            "ssh",
            f"{PI_USER}@{PI_IP}",
            "pkill -f stream.py || true"
        ]
    )

except Exception as e:

    print(
        f"Warning: Failed to kill old stream.py: {e}"
    )

# --------------------------------------------------
# Start stream server
# --------------------------------------------------

print("Starting stream server...")

subprocess.Popen(
    [
        "ssh",
        f"{PI_USER}@{PI_IP}",
        f"python3 {PI_STREAM_SCRIPT}"
    ]
)

# --------------------------------------------------
# Wait for stream server
# --------------------------------------------------

print("Waiting for stream server...")

while True:

    try:

        client_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        client_socket.connect(
            (PI_IP, PORT)
        )

        print("Connected to stream server.")
        break

    except (
        ConnectionRefusedError,
        TimeoutError,
        OSError
    ):

        print(
            "Stream server unavailable. Retrying in 2 seconds..."
        )

        time.sleep(2)

# --------------------------------------------------
# Receive video stream
# --------------------------------------------------

data = b""
payload_size = struct.calcsize("Q")

try:

    while True:

        while len(data) < payload_size:

            packet = client_socket.recv(4096)

            if not packet:
                raise RuntimeError(
                    "Connection closed by server"
                )

            data += packet

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]

        msg_size = struct.unpack(
            "Q",
            packed_msg_size
        )[0]

        while len(data) < msg_size:

            packet = client_socket.recv(4096)

            if not packet:
                raise RuntimeError(
                    "Connection closed by server"
                )

            data += packet

        frame_data = data[:msg_size]
        data = data[msg_size:]

        buffer = np.frombuffer(
            frame_data,
            dtype=np.uint8
        )

        frame = cv2.imdecode(
            buffer,
            cv2.IMREAD_COLOR
        )

        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        if frame is None:
            continue

        cv2.imshow(
            "Raspberry Pi Feed",
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == 27:  # ESC
            break

except KeyboardInterrupt:

    pass

finally:

    try:
        client_socket.close()
    except:
        pass

    cv2.destroyAllWindows()

    print("Client shutdown complete.")