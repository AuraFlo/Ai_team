import cv2
from typing import Iterator, Optional

class Camera:
    def __init__(self, index: int = 0):
        self.index = index
        self.cap: Optional[cv2.VideoCapture] = None

    def __enter__(self):
        self.cap = cv2.VideoCapture(self.index)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.cap:
            self.cap.release()

    def frames(self) -> Iterator:
        if not self.cap:
            raise RuntimeError("Camera not opened")
        while True:
            ok, frame = self.cap.read()
            if not ok:
                break
            yield frame
