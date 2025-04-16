import cv2
import face_recognition
from picamera2 import Picamera2

class FacialTracker:
    def __init__(self):
        self.mode = "sentry"
        self.face_detected = False  # New status flag
        self.camera = Picamera2()
        self.camera.configure(self.camera.create_preview_configuration(main={"size": (640, 480)}))
        self.camera.start()

    def set_mode(self, mode):
        self.mode = mode

    def gen_frames(self):
        while True:
            frame = self.camera.capture_array()
            
            # Add face detection visualization
            if self.face_detected:
                cv2.putText(frame, "FACE DETECTED", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            
            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    def start_tracking(self, motor):
        while True:
            frame = self.camera.capture_array()
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.face_detected = False  # Reset flag
            
            if self.mode == "sentry":
                face_locations = face_recognition.face_locations(rgb_frame, model="hog")
                if face_locations:
                    self.face_detected = True
                    top, right, bottom, left = face_locations[0]
                    x = int((left + right) / 2)
                    y = int((top + bottom) / 2)
                    motor.move(x, y)
                    
                    # Store coordinates for visualization
                    self.last_face_coords = (left, top, right, bottom)
