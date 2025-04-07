from flask import Flask, Response, render_template
import cv2
import mediapipe as mp
import threading

app = Flask(__name__)

# Initialize Mediapipe Face Detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.7)


# Multi-threaded Camera Capture
class VideoStream:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.camera.set(cv2.CAP_PROP_FPS, 15)
        self.frame = None
        self.running = True
        threading.Thread(target=self.update_frame, daemon=True).start()

    def update_frame(self):
        while self.running:
            success, frame = self.camera.read()
            if success:
                self.frame = frame

    def get_frame(self):
        return self.frame


video_stream = VideoStream()


def generate_frames():
    while True:
        frame = video_stream.get_frame()
        if frame is None:
            continue

        frame = cv2.resize(frame, (640, 480))  # Reduce size for speed
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rgb_frame = cv2.cvtColor(gray_frame, cv2.COLOR_GRAY2RGB)

        results = face_detection.process(rgb_frame)

        if results.detections:
            for detection in results.detections:
                bboxC = detection.location_data.relative_bounding_box
                h, w, _ = frame.shape
                x, y, width, height = (
                    bboxC.xmin * w,
                    bboxC.ymin * h,
                    bboxC.width * w,
                    bboxC.height * h,
                )
                cv2.rectangle(
                    frame,
                    (int(x), int(y)),
                    (int(x + width), int(y + height)),
                    (255, 0, 0),
                    2,
                )

        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4010, threaded=True)
