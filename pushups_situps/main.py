from mock_gpio import ButtonInput
from pushup_scoring import run_pushup_session
from bicep_curl import run_bicep_curl_session
from session_logger import save_session_log
from motivational import print_random_quote
from shutdown_handler import shutdown_system

def main():
    button = ButtonInput()
    print("AuraFlo Lite - Edge AI Version\nPress A/B/C/D to simulate buttons.")

    while True:
        key = button.wait_for_keypress()
        if key == 'A':
            mode = input("Enter mode (pushup/bicep): ").strip().lower()
            if mode == 'pushup':
                run_pushup_session()
            elif mode == 'bicep':
                run_bicep_curl_session()
        elif key == 'B':
            save_session_log()
        elif key == 'C':
            print_random_quote()
        elif key == 'D':
            shutdown_system()

if __name__ == "__main__":
    main()