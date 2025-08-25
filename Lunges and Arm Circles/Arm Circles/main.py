import cv2
from model import detect_keypoints, to_pixels
from skeleton import COCO_KP, SKELETON
from utils import line, circ, put_hindi_text
from arm_state import ArmState, update_arm_circle
from config import MIN_CONF

right_state, left_state = ArmState(), ArmState()

cap = cv2.VideoCapture(0)
cv2.namedWindow("Arm Circles", cv2.WINDOW_NORMAL)
draw_skeleton = True

while True:
    ok, frame = cap.read()
    if not ok: break
    h, w = frame.shape[:2]
    kps_norm = detect_keypoints(frame)
    kps = to_pixels(kps_norm, w, h)

    def ok_j(*idxs): return all(kps[i,2] >= MIN_CONF for i in idxs)

    if draw_skeleton:
        for (i,j) in SKELETON:
            if ok_j(i,j): line(frame, kps[i,:2], kps[j,:2], (150,150,150), 2)
        for i in range(17):
            if kps[i,2] >= MIN_CONF: circ(frame, kps[i,:2], (180,180,180), 4)

    # RIGHT
    if ok_j(COCO_KP["right_shoulder"], COCO_KP["right_elbow"], COCO_KP["right_wrist"]):
        rs,re,rw = kps[5,:2], kps[8,:2], kps[10,:2]
        r_ang,r_elbow,r_rad,r_status,r_score = update_arm_circle(right_state, rs,re,rw)
        cv2.putText(frame, f"Right Reps: {right_state.reps} | {r_status}", (20,40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0) if r_status=="Good" else (0,0,255),2)

    # LEFT
    if ok_j(COCO_KP["left_shoulder"], COCO_KP["left_elbow"], COCO_KP["left_wrist"]):
        ls,le,lw = kps[6,:2], kps[7,:2], kps[9,:2]
        l_ang,l_elbow,l_rad,l_status,l_score = update_arm_circle(left_state, ls,le,lw)
        cv2.putText(frame, f"Left Reps: {left_state.reps} | {l_status}", (20,70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0) if l_status=="Good" else (0,0,255),2)

    #frame = put_hindi_text(frame, "निर्देश: सीधे खड़े हों, बाँहें सीधी रखें, बड़े गोल घुमाएँ।", (20,h-40))
    cv2.imshow("Arm Circles", frame)

    key = cv2.waitKey(1)&0xFF
    if key==ord('q'): break
    if key==ord('s'): draw_skeleton = not draw_skeleton

cap.release()
cv2.destroyAllWindows()
