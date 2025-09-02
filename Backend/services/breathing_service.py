# app/services/breathing_service.py
import cv2
import numpy as np
import time
from collections import deque
from scipy.signal import butter, filtfilt, find_peaks, detrend
from typing import Dict


class BreathingEstimator:
    def __init__(self, fs_est: float = 30.0, buffer_seconds: int = 20, analysis_rate_hz: int = 2):
        """
        fs_est: estimated frames per second (default 30 for webcam)
        buffer_seconds: how many seconds of signal history to keep
        analysis_rate_hz: how often (Hz) to update breathing analysis
        """
        self.FS_EST = fs_est
        self.BUFFER_LEN = int(buffer_seconds * fs_est)
        self.ANALYSIS_RATE_HZ = analysis_rate_hz

        self.signal_buffer = deque(maxlen=self.BUFFER_LEN)
        self.ts_buffer = deque(maxlen=self.BUFFER_LEN)

        self.last_analysis_t = time.time()
        self.breath_rate_ema = 0.0
        self.have_bpm = False

    def _bandpass_filter(self, sig, fs, low=0.2, high=0.75, order=3):
        """
        Band-pass filter (0.2–0.75 Hz = ~12–45 breaths/min)
        """
        nyq = 0.5 * fs
        if nyq <= 0 or low >= high or (high / nyq) >= 1:
            return sig
        b, a = butter(order, [low / nyq, high / nyq], btype="band")
        return filtfilt(b, a, sig)

    def process_frame(self, frame_bgr, age: int = 25) -> Dict:
        """
        Process one video frame to update breathing estimation.
        Input: OpenCV BGR frame
        Output: dict {success, bpm, irregular, reason}
        """
        gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # crude ROI (center area; can be replaced by face detector later)
        roi = gray[h // 3:h * 2 // 3, w // 3:w * 2 // 3]
        now = time.time()

        if roi.size > 0:
            self.signal_buffer.append(float(np.mean(roi)))
            self.ts_buffer.append(now)

        result = {"success": False, "bpm": None, "irregular": None, "reason": None}

        if (
            len(self.signal_buffer) == self.signal_buffer.maxlen
            and (now - self.last_analysis_t) >= (1.0 / self.ANALYSIS_RATE_HZ)
        ):
            self.last_analysis_t = now
            dur = self.ts_buffer[-1] - self.ts_buffer[0]
            fs = (len(self.ts_buffer) / dur) if dur > 0 else self.FS_EST

            sig = np.array(self.signal_buffer, dtype=np.float32)
            sig = detrend(sig, type="linear")
            filt = self._bandpass_filter(sig, fs=fs)

            # detect breathing peaks
            peaks, _ = find_peaks(filt, distance=max(1, int(fs * 0.8)))
            bpm_instant = (len(peaks) / dur) * 60.0 if dur > 0 else 0.0

            # exponential moving average
            if self.have_bpm:
                self.breath_rate_ema = 0.25 * bpm_instant + 0.75 * self.breath_rate_ema
            else:
                self.breath_rate_ema = bpm_instant
                self.have_bpm = True

            bpm = float(self.breath_rate_ema)

            # ✅ Age-aware thresholds
            if age < 40:
                normal_range = (12, 20)  # adult range
            else:
                normal_range = (10, 18)  # older adults

            irregular = bpm < normal_range[0] or bpm > normal_range[1]
            reason = None
            if irregular:
                if bpm < normal_range[0]:
                    reason = f"Breathing too slow (<{normal_range[0]} bpm for age {age})"
                elif bpm > normal_range[1]:
                    reason = f"Breathing too fast (>{normal_range[1]} bpm for age {age})"

            result = {
                "success": True,
                "bpm": bpm,
                "irregular": irregular,
                "reason": reason,
            }

        return result
