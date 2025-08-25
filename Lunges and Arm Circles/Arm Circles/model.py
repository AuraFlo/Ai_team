import tensorflow as tf
import tensorflow_hub as hub
import cv2
import numpy as np
from config import MODEL_HANDLE, INPUT_RES

print("Loading MoveNet…")
movenet = hub.load(MODEL_HANDLE).signatures["serving_default"]

def detect_keypoints(frame_bgr):
    img_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    inp = tf.image.resize_with_pad(tf.expand_dims(img_rgb, 0), INPUT_RES, INPUT_RES)
    inp = tf.cast(inp, dtype=tf.int32)
    out = movenet(inp)
    return out["output_0"].numpy()[0, 0, :, :]

def to_pixels(kps_norm, w, h):
    xy = np.zeros((17,3), dtype=np.float32)
    xy[:,0] = kps_norm[:,1] * w
    xy[:,1] = kps_norm[:,0] * h
    xy[:,2] = kps_norm[:,2]
    return xy
