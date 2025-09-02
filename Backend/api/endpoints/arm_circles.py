import cv2
from fastapi import APIRouter
from app.services.armCircles_service import ArmCirclesService

# Create router for FastAPI
router = APIRouter()

# API endpoint (for backend integration)
@router.get("/")
async def get_arm_circles():
    """
    Simple test endpoint for Arm Circles exercise.
    """
    return {"message": "Arm Circles endpoint is working!"}


# ---- Local Runner (OpenCV) ----
def run_arm_circles():
    """
    Run Arm Circles detection locally using OpenCV webcam feed.
    """
    arm_circles_service = ArmCirclesService()
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Process the frame through the service
        frame, feedback = arm_circles_service.process(frame)

        # Show feedback on the screen
        cv2.putText(frame, feedback, (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Arm Circles Exercise", frame)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# Allow running standalone
if __name__ == "__main__":
    run_arm_circles()