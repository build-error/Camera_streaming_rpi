import socket
import struct
import cv2

from camera import Camera


HOST = "0.0.0.0"
PORT = 9999


camera = Camera(
    width=640,
    height=480
)

server_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

server_socket.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)

server_socket.bind(
    (HOST, PORT)
)

server_socket.listen(1)

print(f"Streaming server started on {HOST}:{PORT}")

try:

    while True:

        print("Waiting for client...")

        conn, addr = server_socket.accept()

        print(f"Client connected: {addr}")

        try:

            while True:

                ret, frame = camera.read()

                if not ret:
                    continue

                success, buffer = cv2.imencode(
                    ".jpg",
                    frame,
                    [
                        cv2.IMWRITE_JPEG_QUALITY,
                        80
                    ]
                )

                if not success:
                    continue

                data = buffer.tobytes()

                message = (
                    struct.pack(
                        "Q",
                        len(data)
                    )
                    + data
                )

                conn.sendall(message)

        except (
            BrokenPipeError,
            ConnectionResetError,
            ConnectionAbortedError
        ):

            print(
                f"Client disconnected: {addr}"
            )

        except Exception as e:

            print(
                f"Streaming error: {e}"
            )

        finally:

            try:
                conn.close()
            except:
                pass

            print(
                "Waiting for next client..."
            )

except KeyboardInterrupt:

    print(
        "\nStopping streaming server..."
    )

finally:

    try:
        camera.release()
    except:
        pass

    try:
        server_socket.close()
    except:
        pass

    print(
        "Server shutdown complete."
    )
