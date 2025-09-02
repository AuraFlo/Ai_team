import cv2, threading
from movemodel import MoveNet

from angl import calculate_angle, flag_knee_error

from database import PoseDB
from ui import PoseUI

# Initialize components
model = MoveNet()
db = PoseDB()
ui = PoseUI()
cap = cv2.VideoCapture(0)

session_id = 1
exercise = "squat"
suggestions = {"knee_error": "Try hamstring stretches to support knee alignment."}

def process_frame():
    ret, frame = cap.read()
    if not ret:
        return
    keypoints = model.detect(frame)
    error, angle = flag_knee_error(keypoints, side="left")
    db.log_error(session_id, exercise, "left_knee", angle, error)
    if error:
        ui.show_alert("Knee hyperextension detected")
        threading.Timer(1.5, lambda: ui.show_alert(suggestions["knee_error"])).start()
    ui.show_frame(frame)

if __name__ == "__main__":
    ui.start(process_frame)
