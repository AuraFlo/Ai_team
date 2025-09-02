import cv2
import numpy as np
import tensorflow as tf
import os
model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "movenet.tflite"))

class PoseEstimator:
    def __init__(self, model_path):
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def detect(self, frame):
        image = cv2.resize(frame, (192, 192))
        input_tensor = np.expand_dims(image.astype(np.uint8), axis=0)
        self.interpreter.set_tensor(self.input_details[0]['index'], input_tensor)
        self.interpreter.invoke()
        keypoints = self.interpreter.get_tensor(self.output_details[0]['index'])[0][0]

        height, width, _ = frame.shape
        return [(int(kp[1] * width), int(kp[0] * height)) for kp in keypoints]