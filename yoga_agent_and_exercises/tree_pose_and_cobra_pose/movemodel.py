import tensorflow as tf
import numpy as np
import cv2

class MoveNet:
    def __init__(self, model_path="movenet_lightning.tflite"):
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def detect(self, frame):
        img = cv2.resize(frame, (192, 192))
        img = np.expand_dims(img, axis=0).astype(np.uint8)
        self.interpreter.set_tensor(self.input_details[0]['index'], img)
        self.interpreter.invoke()
        return self.interpreter.get_tensor(self.output_details[0]['index'])[0][0]

    def detect_pose(self, frame):  # ✅ Add this method
        return self.detect(frame)
