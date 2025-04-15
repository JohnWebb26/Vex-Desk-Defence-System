from flask import Flask, Response, render_template, jsonify
from picamera2 import Picamera2
from libcamera import Transform
import cv2
import numpy as np
import face_recognition
import os
import math
import time

app = Flask(__name__)

# Camera configuration
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(
    main={"size": (1280, 720)},
    transform=Transform(hflip=True, vflip=True)
)
picam2.configure(preview_config)
picam2.start()

# Face detection parameters
FACE_DETECTION_SCALE = 0.5
MIN_FACE_SIZE = 80
TARGET_FACE_HEIGHT = 0.20  # meters

# Known faces setup
KNOWN_FACES_DIR = "known_faces"
known_face_encodings = []
known_face_names = []

def load_known_faces():
    global known_face_encodings, known_face_names
    for name in os.listdir(KNOWN_FACES_DIR):
        dir_path = os.path.join(KNOWN_FACES_DIR, name)
        if os.path.isdir(dir_path):
            for filename in os.listdir(dir_path):
                image = face_recognition.load_image_file(os.path.join(dir_path, filename))
                encoding = face_recognition.face_encodings(image, model="large")[0]
                known_face_encodings.append(encoding)
                known_face_names.append(name)

load_known_faces()

def calculate_distance(face_height_pixels):
    focal_length = 600  # Calibrate for your camera
    return (TARGET_FACE_HEIGHT * focal_length) / face_height_pixels

def detect_faces(frame):
    small_frame = cv2.resize(frame, (0, 0), fx=FACE_DETECTION_SCALE, fy=FACE_DETECTION_SCALE)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    
    face_locations = face_recognition.face_locations(
        rgb_small_frame,
        model="cnn" if FACE_DETECTION_SCALE >= 0.5 else "hog"
    )
    
    return [
        tuple(np.multiply(loc, 1/FACE_DETECTION_SCALE).astype(int))
        for loc in face_locations
        if (loc[2] - loc[0]) > MIN_FACE_SIZE/FACE_DETECTION_SCALE
    ]

last_frame_time = time.time()
frame_counter = 0
fps = 0

def process_frame(frame):
    global fps, frame_counter, last_frame_time
    
    frame_counter += 1
    if time.time() - last_frame_time >= 1:
        fps = frame_counter
        frame_counter = 0
        last_frame_time = time.time()
    
    face_data = []
    face_locations = detect_faces(frame)
    
    if face_locations:
        face_encodings = face_recognition.face_encodings(
            cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
            face_locations
        )
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            distance = 0
            
            if True in matches:
                best_match_index = np.argmin(face_recognition.face_distance(
                    known_face_encodings, face_encoding))
                name = known_face_names[best_match_index]
            
            face_height = bottom - top
            distance = calculate_distance(face_height)
            center_x = (left + right) // 2
            center_y = (top + bottom) // 2
            
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, f"{name} {distance:.1f}m", (left + 6, bottom - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            face_data.append({
                "name": name,
                "distance": round(distance, 2),
                "position": (center_x, center_y)
            })
    
    cv2.putText(frame, f"FPS: {fps}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    return frame, face_data

def generate_frames():
    while True:
        try:
            frame = picam2.capture_array()
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            processed_frame, _ = process_frame(frame_bgr)
            ret, buffer = cv2.imencode('.jpg', processed_frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"Frame generation error: {str(e)}")
            time.sleep(0.1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/face_data')
def face_data():
    frame = picam2.capture_array()
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    _, face_data = process_frame(frame_bgr)
    return jsonify(face_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4010, threaded=True)
