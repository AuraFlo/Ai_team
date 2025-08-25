import cv2, math, os
import numpy as np
from PIL import ImageFont, ImageDraw, Image

def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
    ang = abs(ang)
    return 360 - ang if ang > 180 else ang

def polar_angle_deg(origin, point):
    dy, dx = point[1]-origin[1], point[0]-origin[0]
    ang = math.degrees(math.atan2(dy, dx))
    return ang+360 if ang < 0 else ang

def ang_delta(a, b):
    d = b - a
    if d > 180: d -= 360
    if d <= -180: d += 360
    return d

def line(frame, p, q, color, thick=3):
    cv2.line(frame, (int(p[0]), int(p[1])), (int(q[0]), int(q[1])), color, thick)

def circ(frame, p, color, r=5):
    cv2.circle(frame, (int(p[0]), int(p[1])), r, color, -1)

def find_hindi_font():
    for p in [
        r"C:\Windows\Fonts\Nirmala.ttf",
        r"C:\Windows\Fonts\Mangal.ttf",
        r"C:\Windows\Fonts\NirmalaUI.ttf",
        r"C:\Windows\Fonts\ARIALUNI.TTF"
    ]:
        if os.path.exists(p): return p
    return None

HINDI_FONT_PATH = find_hindi_font()

def put_hindi_text(frame, text, pos, font_size=24, color=(255,255,255)):
    if HINDI_FONT_PATH is None:
        return frame
    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    font = ImageFont.truetype(HINDI_FONT_PATH, font_size)
    draw.text(pos, text, font=font, fill=color)
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
