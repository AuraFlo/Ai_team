import tensorflow as tf
import urllib.request
import os

# Direct TFLite model URLs
MODELS = {
    "movenet_lightning": "https://tfhub.dev/google/lite-model/movenet/singlepose/lightning/3?lite-format=tflite",
    "movenet_thunder": "https://tfhub.dev/google/lite-model/movenet/singlepose/thunder/3?lite-format=tflite",
    "movenet_multipose": "https://tfhub.dev/google/lite-model/movenet/multipose/lightning/1?lite-format=tflite"
}

SAVE_DIR = "tflite_models"
os.makedirs(SAVE_DIR, exist_ok=True)

def download_tflite_model(name, url):
    filename = os.path.join(SAVE_DIR, f"{name}.tflite")
    if not os.path.exists(filename):
        print(f"⬇️ Downloading {name} from {url} ...")
        urllib.request.urlretrieve(url, filename)
        print(f"✅ Saved: {filename}")
    else:
        print(f"ℹ️ {filename} already exists. Skipping download.")
    return filename

def load_tflite_model(path):
    interpreter = tf.lite.Interpreter(model_path=path)
    interpreter.allocate_tensors()
    print(f"✅ Loaded {path}")
    return interpreter

if __name__ == "__main__":
    interpreters = {}
    for name, url in MODELS.items():
        tflite_path = download_tflite_model(name, url)
        interpreters[name] = load_tflite_model(tflite_path)

    print("\n🎉 All MoveNet models downloaded and loaded successfully!")