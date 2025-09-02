class ButtonInput:
    def wait_for_keypress(self):
        print("Press A (Workout), B (Save), C (Motivate), D (Shutdown): ", end='')
        return input().strip().upper()