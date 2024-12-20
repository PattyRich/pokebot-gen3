import time
import pyautogui

def keep_screen_alive():
    while True:
        pyautogui.press('shift')
        print("Shift pressed", flush=True)
        time.sleep(20)

if __name__ == "__main__":
    keep_screen_alive()