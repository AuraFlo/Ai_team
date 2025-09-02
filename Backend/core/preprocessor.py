import numpy as np

def normalize_keypoints(keypoints, frame_shape):
    """Normalize (x,y) coords to [0,1] based on frame size."""
    h, w = frame_shape[:2]
    normed = []
    for kp in keypoints:
        x, y = kp["x"], kp["y"]
        nx, ny = x / w, y / h
        if np.isnan(nx) or np.isnan(ny):
            nx, ny = 0.0, 0.0
        normed.append({"x": nx, "y": ny, "score": kp.get("score", 1.0)})
    return normed

def create_sequence(buffer, max_len=60):
    """Maintain a rolling buffer of last max_len frames."""
    if len(buffer) >= max_len:
        return np.array(buffer[-max_len:])
    return None
