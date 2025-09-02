import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import cv2

# Load MoveNet Lightning (faster, real-time)
MODEL_URL = "https://tfhub.dev/google/movenet/singlepose/lightning/4"
movenet = hub.load(MODEL_URL)

def detect_landmarks(frame) -> list:
    """
    Detects body landmarks using MoveNet Lightning.
    Args:
        frame: np.ndarray (OpenCV image, shape HxWx3, BGR)
    Returns:
        List[dict] with 17 keypoints (x,y in pixels, score).
    """
    # Convert BGR (cv2) to RGB (TF expects RGB)
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Resize to 192x192 (Lightning requirement)
    input_img = tf.image.resize_with_pad(tf.expand_dims(img, axis=0), 192, 192)
    input_img = tf.cast(input_img, dtype=tf.int32)

    # Run inference
    outputs = movenet.signatures['serving_default'](input_img)
    keypoints = outputs['output_0'].numpy()  # shape: (1,1,17,3)

    h, w, _ = frame.shape
    landmarks = []
    for kp in keypoints[0][0]:
        y, x, conf = kp
        landmarks.append({
            "x": float(x * w),     # pixel coordinate
            "y": float(y * h),
            "score": float(conf)
        })

    return landmarks
