from flask import Flask, render_template, Response, jsonify
from facial_recognition import FacialTracker
from motor_controller import MotorController
import threading

app = Flask(__name__)
tracker = FacialTracker()
motor = MotorController(port='/dev/ttyAMA0', baudrate=9600)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(tracker.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/toggle_mode/<mode>')
def toggle_mode(mode):
    tracker.set_mode(mode)
    return jsonify({"status": "success"})

@app.route('/face_status')
def face_status():
    return jsonify({
        "face_detected": tracker.face_detected,
        "coordinates": getattr(tracker, 'last_face_coords', None)
    })

def run_flask():
    app.run(host='0.0.0.0', port=4010)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    tracker.start_tracking(motor)
