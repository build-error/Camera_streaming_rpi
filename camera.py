import cv2

try:
    from picamera2 import Picamera2
    PICAMERA2_AVAILABLE = True
except ImportError:
    PICAMERA2_AVAILABLE = False


class Camera:

    def __init__(
        self,
        width=640,
        height=480,
        use_picam=True,
        camera_id=0
    ):

        self.camera_type = None

        # ---------------------------------
        # Try Raspberry Pi Camera
        # ---------------------------------

        if use_picam and PICAMERA2_AVAILABLE:

            try:

                self.picam2 = Picamera2()

                self.picam2.configure(
                    self.picam2.create_preview_configuration(
                        main={
                            "size": (width, height),
                            "format": "BGR888"
                        }
                    )
                )

                self.picam2.start()

                self.camera_type = "picamera2"

                print("[INFO] Using Pi Camera")

                return

            except Exception as e:

                print(
                    "[WARN] Pi Camera unavailable:",
                    e
                )

        # ---------------------------------
        # Fall back to USB webcam
        # ---------------------------------

        self.cap = cv2.VideoCapture(camera_id)

        if not self.cap.isOpened():

            raise RuntimeError(
                "No camera detected."
            )

        self.cap.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            width
        )

        self.cap.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            height
        )

        self.camera_type = "usb"

        print(
            f"[INFO] Using USB Webcam ({camera_id})"
        )

    # ---------------------------------
    # Grab frame
    # ---------------------------------

    def read(self):

        if self.camera_type == "picamera2":

            frame = self.picam2.capture_array()

            return True, frame

        ret, frame = self.cap.read()

        return ret, frame

    # ---------------------------------
    # Cleanup
    # ---------------------------------

    def release(self):

        if self.camera_type == "picamera2":

            self.picam2.stop()

        elif self.camera_type == "usb":

            self.cap.release()