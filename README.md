# Camera Streaming: Raspberry Pi 5 → Laptop

A lightweight TCP-based camera streaming framework for transmitting video from a Raspberry Pi 5 (Pi Camera or USB Webcam) to a laptop for real-time computer vision applications.

The Raspberry Pi is responsible only for image acquisition and transmission. All image processing, object detection, tracking, visual servoing, and control algorithms are executed on the laptop.

---

# Repository Structure

```text
Camera_streaming_rpi/
├── camera.py
├── capture_rpi.py
├── README.md
└── stream.py
```

## Files

### camera.py

Camera abstraction layer.

Supported camera sources:

* Raspberry Pi Camera Module (Picamera2)
* USB Webcam

The class automatically selects the available camera source and provides a unified OpenCV-compatible interface.

### stream.py

Streaming server running on the Raspberry Pi.

Responsibilities:

* Acquire frames from the camera
* JPEG compress frames
* Stream frames through a TCP socket

### capture_rpi.py

Streaming client running on the laptop.

Responsibilities:

* Wait for Raspberry Pi connectivity
* Launch `stream.py` remotely through SSH
* Connect to the streaming server
* Receive and decode image frames
* Display the live video stream

---

# System Architecture

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

The Raspberry Pi performs only image acquisition and transmission.

All image processing is performed on the laptop.

---

# Requirements

## Raspberry Pi

* Raspberry Pi 5
* Raspberry Pi OS or Ubuntu 24.04
* Raspberry Pi Camera Module or USB Webcam

## Laptop

* Linux system
* Python 3
* OpenCV
* NumPy

---

# Installation

Clone the repository on both systems:

```bash
git clone <repository-url>
```

Install Python dependencies:

```bash
pip install opencv-python numpy
```

For Raspberry Pi Camera support:

```bash
pip install picamera2
```

---

# Network Configuration

This project assumes a direct Ethernet connection between the Raspberry Pi and the laptop.

## Physical Connection

```text
Laptop <------ Ethernet ------> Raspberry Pi 5
```

## Static IPv4 Configuration

The following IP addresses are used throughout the project:

```text
Laptop IP      : 192.168.10.1
Raspberry Pi IP: 192.168.10.2
Subnet Mask    : 255.255.255.0
Port           : 9999
```

---

## Raspberry Pi Configuration

Identify the Ethernet interface:

```bash
ip link
```

Typically:

```text
eth0
```

Edit the Netplan configuration:

```bash
sudo nano /etc/netplan/01-network-manager-all.yaml
```

Example:

```yaml
network:
  version: 2
  renderer: NetworkManager

  ethernets:
    eth0:
      dhcp4: false
      addresses:
        - 192.168.10.2/24
```

Apply the configuration:

```bash
sudo netplan apply
```

Verify:

```bash
ip addr show eth0
```

Expected:

```text
inet 192.168.10.2/24
```

---

## Laptop Configuration

Identify the Ethernet interface:

```bash
ip link
```

Typical Ethernet interface names:

```text
eno1
enp3s0
enp88s0
eth0
```

The interface name varies depending on the hardware and Linux distribution.

For example, on the development laptop used for this project:

```text
enp88s0
```

was the Ethernet interface.

Assign a static IPv4 address:

```bash
sudo ip addr add 192.168.10.1/24 dev <ethernet_interface>
```

Example:

```bash
sudo ip addr add 192.168.10.1/24 dev enp88s0
```

Verify:

```bash
ip addr show <ethernet_interface>
```

Example:

```bash
ip addr show enp88s0
```

Expected output:

```text
inet 192.168.10.1/24
```

## Connectivity Test

From the laptop:

```bash
ping 192.168.10.2
```

From the Raspberry Pi:

```bash
ping 192.168.10.1
```

Successful communication confirms that the Ethernet link is correctly configured.

---

# SSH Configuration

Verify SSH access from the laptop:

```bash
ssh <username>@192.168.10.2
```

Example:

```bash
ssh hanggu-pi5@192.168.10.2
```

Enable passwordless SSH:

```bash
ssh-copy-id hanggu-pi5@192.168.10.2
```

This allows `capture_rpi.py` to automatically launch the streaming server.

---

# Camera Abstraction Layer

The `Camera` class automatically selects the available camera source.

Priority:

1. Raspberry Pi Camera Module
2. USB Webcam

Example:

```python
from camera import Camera

camera = Camera(
    width=640,
    height=480
)
```

Reading frames:

```python
ret, frame = camera.read()
```

Returned images are OpenCV-compatible BGR images.

This allows the remainder of the code to remain independent of camera hardware.

---

# Starting the Streaming Server

On the Raspberry Pi:

```bash
python3 stream.py
```

Expected output:

```text
Streaming server started on 0.0.0.0:9999
Waiting for client...
```

Once connected:

```text
Client connected: ('192.168.10.1', XXXXX)
```

The server continuously:

1. Captures images from the camera
2. Compresses images using JPEG
3. Sends frames through a TCP socket

---

# Starting the Streaming Client

On the laptop:

```bash
python3 capture_rpi.py
```

The client automatically:

1. Waits for the Raspberry Pi to become reachable
2. Starts `stream.py` remotely through SSH
3. Connects to the streaming server
4. Receives compressed image frames
5. Decodes images using OpenCV
6. Displays the live video stream

Press:

```text
ESC
```

to terminate the application.

---

# Integration with Computer Vision Pipelines

The received frame can be directly used with:

* OpenCV
* Object Detection
* Object Tracking
* Visual Servoing
* SLAM
* Custom Computer Vision Pipelines

Example:

```python
ret, frame = stream.read()

outputs = tracker.track(frame)
```

No modifications to the streaming layer are required.

---

# Performance Notes

Current configuration:

```text
Resolution    : 640 × 480
JPEG Quality  : 80
Transport     : TCP
Port          : 9999
```

This configuration is suitable for:

* Object Tracking
* Object Detection
* Visual Servoing
* SLAM Visualization
* Remote Camera Monitoring

Image resolution and JPEG quality can be modified in:

```text
camera.py
stream.py
```

depending on the desired image quality and available network bandwidth.

---

# Troubleshooting

## Cannot SSH Into Raspberry Pi

Verify SSH is running:

```bash
sudo systemctl status ssh
```

Enable SSH:

```bash
sudo systemctl enable ssh

sudo systemctl start ssh
```

---

## Cannot Connect To Stream

Verify connectivity:

```bash
ping 192.168.10.2
```

Verify the streaming server is running:

```bash
netstat -tlnp | grep 9999
```

Expected:

```text
0.0.0.0:9999
```

---

## Camera Not Detected

List Raspberry Pi cameras:

```bash
rpicam-still --list-cameras
```

List USB cameras:

```bash
v4l2-ctl --list-devices
```

---

## Connection Reset Errors

If the client is closed unexpectedly, the server may display:

```text
BrokenPipeError
ConnectionResetError
```

This is normal behavior and simply indicates that the client disconnected.

The server automatically returns to:

```text
Waiting for client...
```

and is ready for the next connection.

---

# Typical Workflow

1. Connect Raspberry Pi and laptop via Ethernet.
2. Verify connectivity:

```bash
ping 192.168.10.2
```

3. Verify SSH access:

```bash
ssh hanggu-pi5@192.168.10.2
```

4. Run:

```bash
python3 capture_rpi.py
```

5. The client automatically:

   * Waits for Raspberry Pi connectivity
   * Launches the streaming server
   * Connects to the video stream

6. Begin image processing on the laptop.

---

# License

This project is intended for research, robotics, and educational purposes.