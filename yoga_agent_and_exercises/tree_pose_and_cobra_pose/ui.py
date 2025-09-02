import tkinter as tk
import cv2
from PIL import Image, ImageTk

class PoseUI:
    def __init__(self, width=640, height=480):
        self.root = tk.Tk()
        self.root.title("MoveNet Injury Prevention")
        self.width, self.height = width, height

        self.left_label = tk.Label(self.root)
        self.left_label.pack(side="left")
        self.alert_label = tk.Label(self.root, text="", fg="red", font=("Arial", 16))
        self.alert_label.pack(side="right")

    def show_frame(self, frame):
        frame = cv2.resize(frame, (self.width, self.height))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(frame))
        self.left_label.configure(image=img)
        self.left_label.image = img

    def show_alert(self, message, duration=2000):
        self.alert_label.config(text=message)
        self.root.after(duration, lambda: self.alert_label.config(text=""))

    def start(self, update_fn, delay=30):
        def loop():
            update_fn()
            self.root.after(delay, loop)
        loop()
        self.root.mainloop()
