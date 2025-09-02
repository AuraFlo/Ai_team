# 🫁 Exercise Breathing Monitor (Edge)

This project is a **real-time breathing rate monitoring system** built using **OpenCV, signal processing, and live plotting**.  
It detects a user’s face via webcam, extracts subtle intensity changes from a region of interest (ROI) near the chest/neck, and estimates the **breaths per minute (BPM)**.  

It also provides **irregular breathing detection** with conditions like:
- 🚨 Rate out of range  
- 🚨 Inconsistent rhythm  
- 🚨 Shallow breathing  

Optionally, a live **waveform plot** of the breathing signal is displayed alongside the video feed.

---

## ⚡ Features
- Face detection & tracking with OpenCV (Haar cascades + CSRT/KCF/MOSSE trackers).  
- Real-time breathing signal extraction.  
- Bandpass filtering + detrending to clean signal.  
- Peak detection for estimating breathing rate (BPM).  
- Adaptive analysis modes: **Strict** ↔ **Relaxed** depending on stability.  
- Warnings for irregular breathing.  
- Live Matplotlib visualization of waveform & detected peaks.  
- Works on edge devices (CPU-only, lightweight).

---

## 📦 Requirements
Install dependencies via `pip`:

```bash
pip install opencv-python numpy scipy matplotlib
```

---

## ▶️ Usage
Run the script directly:

```bash
python breathing_monitor_plot3.py
```

- Press **`q`** to quit.  
- A window will open showing:
  - Webcam feed with breathing rate overlay.  
  - Warnings if irregular breathing is detected.  
- If enabled (`SHOW_PLOT = True`), a live breathing waveform will appear.

---

## ⚙️ Configurable Parameters (in script)
| Parameter | Default | Description |
|-----------|---------|-------------|
| `CAM_INDEX` | `0` | Camera index for webcam. |
| `SET_RESOLUTION` | `True` | Force resolution setting. |
| `WIDTH, HEIGHT` | `640, 480` | Frame resolution. |
| `SHOW_PLOT` | `True` | Show real-time waveform plot. |
| `ANALYSIS_RATE_HZ` | `2` | Frequency of analysis updates. |
| `BUFFER_SECONDS` | `20` | Signal buffer size. |
| `LOW_CUT, HIGH_CUT` | `0.2, 0.75` | Bandpass filter cutoffs (Hz). |
| `EMA_ALPHA` | `0.25` | Exponential moving average smoothing. |

---

## 🖥️ Output
- Video window with:
  - ✅ Breathing Rate (BPM)  
  - ✅ Mode: Strict / Relaxed  
  - ⚠️ Warning messages if irregular breathing detected  
  - ⚠️ “No face detected” if tracking fails  

- Optional live **breathing waveform plot** with detected peaks.

---

## 🚀 Future Improvements
- Integrate **whisper-based voice feedback**.  
- Add **logging of breathing trends** over time.  
- Deploy as a **lightweight mobile/edge app**.  
