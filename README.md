# Camera Streaming: Raspberry Pi 5 → Laptop

## Repository Structure

```text
Camera_streaming_rpi/
├── camera.py
├── capture_rpi.py
├── README.md
└── stream.py
```

This repository provides a lightweight TCP-based camera streaming system for sending video from a Raspberry Pi 5 (or USB webcam) to a laptop over a direct Ethernet connection.

The Raspberry Pi acts as the streaming server, while the laptop acts as the client.

---

## Architecture

```text
Raspberry Pi Camera / USB Webcam
                │
                ▼
          camera.py
                │
                ▼
          stream.py
                │
          TCP Socket
                │
        Ethernet Link
                │
                ▼
        capture_rpi.py
                │
                ▼
      OpenCV / Tracking /
      Detection Pipeline
```

The Raspberry Pi is responsible only for image acquisition and transmission.

All image processing, tracking, object detection, visual servoing, and control algorithms are executed on the laptop.

---

## Camera Abstraction

The `Camera` class automatically selects the available camera source.

Priority:

1. Raspberry Pi Camera Module (Picamera2)
2. USB Webcam

Example:

```python
from camera import Camera

camera = Camera(
    width=640,
    height=480
)
```

The camera interface always returns OpenCV-compatible BGR images:

```python
ret, frame = camera.read()
```

This allows the rest of the code to remain independent of the underlying camera hardware.

---

## Starting the Streaming Server (Raspberry Pi)

Run:

```bash
python3 stream.py
```

Expected output:

```text
Streaming server started on 0.0.0.0:9999
Waiting for client...
```

Once a laptop connects:

```text
Client connected: ('192.168.10.1', XXXXX)
```

The server continuously:

1. Captures frames from the camera.
2. Compresses frames using JPEG.
3. Sends the encoded frames through a TCP socket.

---

## Starting the Client (Laptop)

Run:

```bash
python3 capture_rpi.py
```

The client:

1. Waits for the Raspberry Pi to become reachable.
2. Launches `stream.py` remotely using SSH.
3. Connects to the TCP streaming server.
4. Receives compressed frames.
5. Decodes the frames using OpenCV.
6. Displays the live video stream.

Press:

```text
ESC
```

to close the viewer.

---

## Network Configuration

Default configuration:

```text
Laptop IP      : 192.168.10.1
Raspberry Pi IP: 192.168.10.2
Port           : 9999
Protocol       : TCP
```

The Ethernet setup procedure is documented earlier in this README.

---

## SSH Access

Verify SSH connectivity:

```bash
ssh <username>@192.168.10.2
```

Example:

```bash
ssh hanggu-pi5@192.168.10.2
```

Passwordless SSH can be configured using:

```bash
ssh-copy-id hanggu-pi5@192.168.10.2
```

This allows `capture_rpi.py` to automatically start `stream.py` on the Raspberry Pi.

---

## Integration with Tracking Systems

The received frame can be directly used with:

* OpenCV
* OSTrack
* MixFormer
* YOLO
* ByteTrack
* Visual Servoing Pipelines
* ROS 2 Nodes

Example:

```python
frame = receive_frame()

outputs = tracker.track(frame)
```

No modifications are required to the streaming system.

---

## Performance Notes

Current configuration:

```text
Resolution    : 640 × 480
JPEG Quality  : 80
Transport     : TCP
```

This configuration is suitable for:

* Object tracking
* Visual servoing
* SLAM visualization
* Remote camera monitoring

Higher resolutions can be configured in `camera.py` and `stream.py` if additional bandwidth is available.

---

## Typical Workflow

1. Connect Raspberry Pi and laptop via Ethernet.
2. Verify connectivity using:

```bash
ping 192.168.10.2
```

3. Run:

```bash
python3 capture_rpi.py
```

4. The client automatically:

   * Waits for the Raspberry Pi.
   * Starts the streaming server.
   * Connects to the video stream.

5. Begin tracking, detection, or visual servoing on the laptop.
