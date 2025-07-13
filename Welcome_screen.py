import tkinter as tk
from PIL import Image, ImageTk
import os

class AurWelcomeScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Welcome - AuraFlo")
        self.attributes('-fullscreen', True)  # Fullscreen window
        self.configure(bg="black")

        # Escape key to exit
        self.bind("<Escape>", lambda e: self.destroy())

        # Get full screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # ✅ Path to your welcome image
        image_path = r"C:\Users\91800\Desktop\logo.png"  # Update as needed

        if not os.path.exists(image_path):
            print(f"❌ Image not found at: {image_path}")
            self.destroy()
            return

        # ✅ Load and resize the image to match full screen
        image = Image.open(image_path).resize((screen_width, screen_height), Image.Resampling.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(image)

        # ✅ Display image
        self.image_label = tk.Label(self, image=self.bg_image, bg="black")
        self.image_label.pack(fill="both", expand=True)

        # ✅ Bind click anywhere to continue
        self.bind("<Button-1>", self.proceed)

    def proceed(self, event=None):
        print("✅ Screen clicked. Proceeding to main application...")
        self.destroy()
        self.launch_main_screen()

    def launch_main_screen(self):
        next_window = tk.Tk()
        next_window.title("AuraFlo Dashboard")
        next_window.geometry("800x600")  # Adjust as needed
        tk.Label(next_window, text="🌿 AuraFlo Main App", font=("Helvetica", 24, "bold")).pack(expand=True)
        next_window.mainloop()

if __name__ == "__main__":
    app = AurWelcomeScreen()
    app.mainloop()
