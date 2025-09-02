import platform

def shutdown_system():
    confirm = input("Shutdown system? (y/n): ")
    if confirm.lower() == 'y':
        if platform.system() == 'Linux':
            import os
            os.system("sudo shutdown now")
        else:
            print("Simulated shutdown (Mac test environment)")
    else:
        print("Shutdown cancelled.")