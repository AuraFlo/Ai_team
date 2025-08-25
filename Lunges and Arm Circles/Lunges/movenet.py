import tensorflow as tf
import tensorflow_hub as hub
from config import MODEL_HANDLE, INPUT_RES

# Load MoveNet model
movenet = hub.load(MODEL_HANDLE)

def detect_pose(frame):
    """Run MoveNet on frame, return keypoints (1,17,3)."""
    img = tf.image.resize_with_pad(tf.expand_dims(frame, axis=0), INPUT_RES, INPUT_RES)
    img = tf.cast(img, dtype=tf.int32)
    outputs = movenet.signatures['serving_default'](img)
    return outputs['output_0'].numpy().reshape((1, 17, 3))
