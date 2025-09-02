# app/core/report_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import os
from ..db import crud


def generate_session_report(session_id: int) -> str:
    """
    Generate a PDF report for a workout session.
    Includes: reps, accuracy, emotion, breathing rate, irregularity.
    """
    os.makedirs("logs", exist_ok=True)
    path = f"logs/session_{session_id}.pdf"
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4

    # Fetch session + events
    s = crud.get_session(session_id)
    events = crud.get_events(session_id)

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, f"Auraflo Session Report #{session_id}")

    # Basic info
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 90, f"Workout: {s.workout_type}")
    c.drawString(50, height - 110, f"Total Events: {len(events)}")

    # Table data
    table_data = [["Time", "Reps", "Accuracy", "Emotion", "Breathing (BPM)", "Irregular?"]]

    for e in events[:25]:  # only first 25 events to fit on page
        table_data.append([
            str(e.timestamp),
            str(e.reps),
            f"{e.accuracy:.1f}" if e.accuracy else "-",
            e.emotion or "-",
            f"{e.breathing_bpm:.1f}" if e.breathing_bpm else "-",
            "Yes" if e.breathing_irregular else "No"
        ])

    # Build table
    table = Table(table_data, colWidths=[100, 50, 60, 80, 90, 70])
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ])
    table.setStyle(style)

    # Place table
    table.wrapOn(c, width, height)
    table.drawOn(c, 50, height - 400)

    c.save()
    return path
