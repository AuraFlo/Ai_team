import cv2
import numpy as np
from scipy.signal import butter, filtfilt, find_peaks, detrend
from collections import deque
import time
import matplotlib.pyplot as plt

CAM_INDEX = 0
SET_RESOLUTION = True
WIDTH, HEIGHT = 640, 480
SHOW_PLOT = True
ANALYSIS_RATE_HZ = 2
BUFFER_SECONDS = 20
LOW_CUT, HIGH_CUT = 0.2, 0.75
EMA_ALPHA = 0.25

def bandpass_filter(sig, fs, low=LOW_CUT, high=HIGH_CUT, order=3):
    nyq = 0.5 * fs
    if nyq <= 0 or (low/nyq) >= 1 or (high/nyq) >= 1 or low >= high:
        return sig
    b, a = butter(order, [low/nyq, high/nyq], btype='band')
    return filtfilt(b, a, sig)

def draw_text_with_bg(img, text, pos, font=cv2.FONT_HERSHEY_SIMPLEX,
                      font_scale=0.9, text_color=(255,255,255),
                      bg_color=(0,0,0), thickness=2, alpha=0.45, padding=6):
    x, y = pos
    (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
    th = int(th * 1.2)
    overlay = img.copy()
    cv2.rectangle(overlay, (x - padding, y - th - padding),
                  (x + tw + padding, y + padding), bg_color, -1)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
    cv2.putText(img, text, (x, y), font, font_scale, text_color, thickness, cv2.LINE_AA)

def create_tracker():
    for ctor in [
        getattr(cv2, "TrackerCSRT_create", None),
        getattr(cv2, "TrackerKCF_create", None),
        getattr(cv2, "TrackerMOSSE_create", None),
    ]:
        if callable(ctor):
            try:
                return ctor()
            except Exception:
                pass
    return None

print("Starting camera…")
cap = cv2.VideoCapture(CAM_INDEX)
if not cap.isOpened():
    print("Error: Could not open camera.")
    raise SystemExit(1)

if SET_RESOLUTION:
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 30)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
if face_cascade.empty():
    print("Error: Haar cascade not found.")
    raise SystemExit(1)

FS_EST = 30.0
BUFFER_LEN = int(BUFFER_SECONDS * FS_EST)
signal_buffer = deque(maxlen=BUFFER_LEN)
ts_buffer = deque(maxlen=BUFFER_LEN)

breath_rate_ema = 0.0
have_bpm = False
irregular = False
reason = ""
use_relaxed = False
stable_counter = 0
last_analysis_t = time.time()

strict_rate_range = (22, 40)
relaxed_rate_range = (20, 42)
strict_interval_var = 0.2
relaxed_interval_var = 0.25
strict_amplitude_var = 0.5
relaxed_amplitude_var = 0.4

tracker = None
face_box = None

time.sleep(1.0)
print("Camera ready. Press 'q' to quit.")

if SHOW_PLOT:
    plt.ion()
    fig, ax = plt.subplots(figsize=(8, 4))
    line, = ax.plot([], [], label="Breathing Waveform (z-score)")
    peaks_plot, = ax.plot([], [], 'rx', markersize=6, label="Detected Peaks")
    ax.set_ylim(-4, 4)
    ax.set_xlim(0, BUFFER_LEN)
    ax.set_title("Live Breathing Signal")
    ax.set_xlabel("Frame")
    ax.set_ylabel("Amplitude")
    ax.grid(True)
    ax.legend()

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    now = time.time()

    if tracker is None or face_box is None:
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=6, minSize=(80, 80))
        if len(faces) > 0:
            x, y, w, h = sorted(faces, key=lambda f: f[2]*f[3], reverse=True)[0]
            face_box = (x, y, w, h)
            tracker = create_tracker()
            if tracker is not None:
                tracker.init(frame, tuple(face_box))
    else:
        ok, box = tracker.update(frame)
        if ok:
            face_box = tuple(map(int, box))
        else:
            tracker = None
            face_box = None

    if face_box:
        x, y, w, h = face_box
        cv2.rectangle(frame, (x, y), (x + w, y + h), (64, 160, 255), 2)
        roi_y1 = y + int(h * 0.55)
        roi_y2 = y + int(h * 0.85)
        roi_x1 = x + int(w * 0.30)
        roi_x2 = x + int(w * 0.70)
        H, W = gray.shape
        roi_y1 = max(0, min(H, roi_y1)); roi_y2 = max(0, min(H, roi_y2))
        roi_x1 = max(0, min(W, roi_x1)); roi_x2 = max(0, min(W, roi_x2))
        roi = gray[roi_y1:roi_y2, roi_x1:roi_x2]
        if roi.size > 0:
            mean_intensity = float(np.mean(roi))
            signal_buffer.append(mean_intensity)
            ts_buffer.append(now)

    if len(signal_buffer) == signal_buffer.maxlen and (now - last_analysis_t) >= (1.0 / ANALYSIS_RATE_HZ):
        last_analysis_t = now
        duration = ts_buffer[-1] - ts_buffer[0]
        fs = (len(ts_buffer) / duration) if duration > 0 else FS_EST
        if fs < 5:
            fs = FS_EST
        sig = np.array(signal_buffer, dtype=np.float32)
        sig = detrend(sig, type='linear')
        filt = bandpass_filter(sig, fs=fs)
        std = np.std(filt)
        zsig = (filt - np.mean(filt)) / std if std > 1e-6 else filt
        min_distance = max(1, int(fs * 0.8))
        height_thr = 0.2
        prominence_thr = 0.3
        peaks, _ = find_peaks(zsig, distance=min_distance, height=height_thr, prominence=prominence_thr)
        bpm_instant = (len(peaks) / duration) * 60.0 if duration > 0 else 0.0

        if have_bpm:
            breath_rate_ema = EMA_ALPHA * bpm_instant + (1.0 - EMA_ALPHA) * breath_rate_ema
        else:
            breath_rate_ema = bpm_instant
            have_bpm = True

        rate_low, rate_high = (relaxed_rate_range if use_relaxed else strict_rate_range)
        interval_thr = (relaxed_interval_var if use_relaxed else strict_interval_var)
        amplitude_thr = (relaxed_amplitude_var if use_relaxed else strict_amplitude_var)
        irregular = False
        reason = ""

        if not (rate_low <= breath_rate_ema <= rate_high):
            irregular, reason = True, "Rate out of range"

        if len(peaks) > 2:
            intervals = np.diff(peaks) / fs
            interval_var = np.std(intervals) / np.mean(intervals) if np.mean(intervals) > 0 else 0.0
            amplitude_var = np.std(zsig[peaks]) if len(peaks) else 0.0
            if interval_var > interval_thr:
                irregular, reason = True, "Inconsistent rhythm"
            elif amplitude_var < amplitude_thr:
                irregular, reason = True, "Shallow breathing"

        if irregular:
            stable_counter = 0
            use_relaxed = False
        else:
            stable_counter += 1
            if stable_counter > int(10 * ANALYSIS_RATE_HZ):
                use_relaxed = True

        if SHOW_PLOT:
            line.set_ydata(zsig)
            line.set_xdata(np.arange(len(zsig)))
            peaks_plot.set_data(peaks, zsig[peaks])
            ax.set_ylim(np.min(zsig)-0.5, np.max(zsig)+0.5)
            ax.set_xlim(0, len(zsig))
            fig.canvas.draw()
            fig.canvas.flush_events()

    bpm_text = f"Breathing Rate: {breath_rate_ema:.1f} BPM" if have_bpm else "Breathing Rate: --.- BPM"
    mode_text = "Mode: Relaxed" if use_relaxed else "Mode: Strict"
    draw_text_with_bg(frame, bpm_text, (18, 40), text_color=(0, 255, 0), bg_color=(0, 64, 0))
    draw_text_with_bg(frame, mode_text, (18, 75), font_scale=0.8, text_color=(255, 255, 0), bg_color=(48, 48, 0))

    if irregular and have_bpm:
        draw_text_with_bg(frame, f"Warning: {reason}", (18, 110), text_color=(0, 0, 255), bg_color=(48, 0, 0))
    if face_box is None:
        draw_text_with_bg(frame, "No face detected", (18, 145), text_color=(0, 255, 255), bg_color=(0, 48, 48))

    cv2.imshow("Exercise Breathing Monitor (Edge)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
if SHOW_PLOT:
    plt.close('all')