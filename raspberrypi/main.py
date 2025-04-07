import cv2
import mediapipe as mp
from flask import Flask, Response, render_template
import threading

app = Flask(__name__)

mp_face = mp.solutions.face_detection
face_detector = mp_face.FaceDetection(model_selection=1,min_detection_confidence=0.7)

latest_frame = None
lock = threading.Lock()
camera_active = False

def camera_check():
    """Verify a camera is connected"""
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        cap.release()
        return True
    return False

def capture_frames():
    """Thread for continious frame capture and processing"""
    global latest_frame, camera_active
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    camera_active = cap.isOpened()

    while camera_active:
        success, frame = cap.read()
        if not success:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_detector.process(rgb)

        if results.detections:
            bbox = detection.location_data.relative_bounding_box
            confidence = detection.score(0)

            ih, iw, _ = frame.shape
            x = int(bbox.xmin * iw)
            y = int(bbox.ymin * ih)
            w = int(bbox.width * iw)
            h = int(bbox.height * ih)

            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
            cv2.putText(frame, "Confidence:" + str(confidence), (x,y-10), cv2.FRONT_HERSHEY_SIMPLEX, 0.5, (0,255,0),2)

        with lock:
            ret, jpeg = cv2.imencodc(".jpg",frame)
            latest_frame = jpg.tobytes()
    cap.release()

def generate():
    while True:
        with lock:
            if latest_frame is None:
                continue
            frame = latest_frame
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

@app.route('/')
def index():
    return render_template('index.html', camera_ok=camera_check())

@app.route('/video_feed')
def video_feed():
    return Response(generate(),mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    threading.Thread(target=capture_frames, daemon=True).start()
    app.run(host="0.0.0.0", port=3002,threaded=True)
