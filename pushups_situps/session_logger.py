import sqlite3
from datetime import datetime
from reportlab.pdfgen import canvas
import os

def save_session_log():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    workout_type = input("Workout type (pushup/bicep): ")
    reps = input("Reps counted: ")
    score = input("Last score: ")

    conn = sqlite3.connect("auraflo.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS logs (timestamp TEXT, workout TEXT, reps INTEGER, score INTEGER)")
    c.execute("INSERT INTO logs VALUES (?, ?, ?, ?)", (timestamp, workout_type, reps, score))
    conn.commit()
    conn.close()

    if not os.path.exists("logs"):
        os.mkdir("logs")
    pdf_path = f"logs/session_{timestamp.replace(' ', '_').replace(':', '-')}.pdf"
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 750, f"AuraFlo Lite Session Log")
    c.drawString(100, 730, f"Time: {timestamp}")
    c.drawString(100, 710, f"Workout: {workout_type}")
    c.drawString(100, 690, f"Reps: {reps}")
    c.drawString(100, 670, f"Score: {score}")
    c.save()
    print(f"Session log saved to {pdf_path}")