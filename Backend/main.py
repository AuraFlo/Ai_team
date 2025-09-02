from fastapi import FastAPI
from app.api.endpoints import (
    arm_circles,
    bicep_curls,
    high_knees,
    lunges,
    squats,
    pushup,
    yoga_agent,
    movenet,
    reports,
)

app = FastAPI(title="Fitness & Yoga Backend")

# ✅ Include routers
app.include_router(pushup.router, prefix="/pushup", tags=["Pushups"])
app.include_router(squats.router, prefix="/squats", tags=["Squats"])
app.include_router(lunges.router, prefix="/lunges", tags=["Lunges"])
app.include_router(high_knees.router, prefix="/high_knees", tags=["High Knees"])
app.include_router(bicep_curls.router, prefix="/bicep_curls", tags=["Bicep Curls"])
app.include_router(arm_circles.router, prefix="/arm_circles", tags=["Arm Circles"])
app.include_router(yoga_agent.router, prefix="/yoga", tags=["Yoga Agent"])
app.include_router(movenet.router, prefix="/movenet", tags=["MoveNet"])
app.include_router(reports.router, prefix="/reports", tags=["Reports"])


@app.get("/")
def root():
    return {"message": "Welcome to the Fitness & Yoga Backend API 🚀"}