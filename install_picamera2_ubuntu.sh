#!/usr/bin/env bash
# Raspberry Pi 5 on Ubuntu 24.04: Raspberry Pi libcamera (+ Python bindings), rpicam-apps and
# Picamera2, which Ubuntu does not package. Builds into /usr/local; Picamera2 via pip --user.
#   sudo -v && ./install_picamera2_ubuntu.sh        (as the normal user; asks sudo for installs)
# Then: rpicam-hello --list-cameras   and   python3 -c "from picamera2 import Picamera2"
set -euo pipefail
SRC=${SRC:-$HOME/src}
mkdir -p "$SRC"

sudo apt-get update
sudo apt-get install -y git meson ninja-build pkg-config cmake python3-pip \
  libyaml-dev python3-yaml python3-ply python3-jinja2 libgnutls28-dev libssl-dev openssl \
  libdw-dev libudev-dev libevent-dev pybind11-dev python3-pybind11 nlohmann-json3-dev \
  libboost-dev libboost-program-options-dev libdrm-dev libexif-dev libjpeg-dev libtiff-dev \
  libpng-dev libcap-dev

build() {  # build <repo url> <dir> <meson options...>
  local url=$1 dir=$2; shift 2
  [ -d "$SRC/$dir" ] || git clone --depth 1 "$url" "$SRC/$dir"
  cd "$SRC/$dir"
  meson setup build --buildtype=release --prefix=/usr/local --wipe "$@"
  ninja -C build -j3
  sudo ninja -C build install
  sudo ldconfig
}

# libpisp: the Pi 5 image signal processor (needed by libcamera's pisp pipeline)
build https://github.com/raspberrypi/libpisp.git libpisp -Dlogging=disabled
build https://github.com/raspberrypi/libcamera.git libcamera \
  -Dpipelines=rpi/vc4,rpi/pisp -Dipas=rpi/vc4,rpi/pisp -Dv4l2=enabled -Dgstreamer=disabled \
  -Dtest=false -Dlc-compliance=disabled -Dcam=disabled -Dqcam=disabled -Ddocumentation=disabled \
  -Dpycamera=enabled
# kms++ with its Python module pykms: Picamera2 imports it even without a display (python3-kms++ on Pi OS)
build https://github.com/tomba/kmsxx.git kmsxx -Dpykms=enabled -Dkmscube=false -Domap=disabled
build https://github.com/raspberrypi/rpicam-apps.git rpicam-apps \
  -Denable_libav=disabled -Denable_drm=disabled -Denable_egl=disabled -Denable_qt=disabled \
  -Denable_opencv=disabled -Denable_tflite=disabled -Denable_hailo=disabled

# libcamera's Python module lands outside Python's default path: point Python at it.
INIT=$(find /usr/local/lib -path '*-packages/libcamera/__init__.py' | head -1)
[ -n "$INIT" ] || { echo "libcamera Python bindings not found"; exit 1; }
USITE=$(python3 -m site --user-site); mkdir -p "$USITE"
dirname "$(dirname "$INIT")" > "$USITE/libcamera-local.pth"
PYKMS=$(find /usr/local/lib -path '*-packages/pykms/__init__.py' | head -1)
[ -n "$PYKMS" ] || { echo "pykms not found"; exit 1; }
dirname "$(dirname "$PYKMS")" > "$USITE/pykms-local.pth"

# Picamera2; keep the system numpy 1.x (ROS OpenCV is built against it)
python3 -m pip install --user --break-system-packages picamera2 "numpy<2"

rpicam-hello --list-cameras
python3 -c "from picamera2 import Picamera2; print('Picamera2 OK:', Picamera2.global_camera_info())"
