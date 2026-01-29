import os
import sys
import time

# Constants
DIST_DIR = os.path.abspath("bin/Dist/StoryLord") 
INSTALLER_DIR = os.path.abspath("bin/Installer")

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CURSOR_HIDE = "\033[?25l"
    CURSOR_SHOW = "\033[?25h"

def countdown_or_wait(success: bool, seconds: int = 5):
    """On success: auto-continue after countdown. On failure: wait for Enter."""
    # Check if running in a non-interactive environment
    is_ci = os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("CI") == "true"

    if success:
        print(f"{Colors.CURSOR_HIDE}\nSuccess! Continuing in {seconds} seconds...", end="", flush=True)
        for i in range(seconds, 0, -1):
            time.sleep(1)
        print("\n")
    else:
        if is_ci:
            print("\n[CI DETECTED] Build Failed. Exiting immediately without waiting for input.")
            sys.exit(1)
        else:
            set_cursor_visible(True)
            input("\nPress Enter to continue...")
            set_cursor_visible(False)


def get_latest_local_tag():
    import subprocess
    try:
        output = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
        return output
    except:
        return None

def set_cursor_visible(visible: bool):
    """Show or hide the terminal cursor using ANSI and Windows API."""
    import sys
    # ANSI escape codes
    if visible:
        sys.stdout.write('\033[?25h')
    else:
        sys.stdout.write('\033[?25l')
    sys.stdout.flush()

    # Windows-specific ctypes fallback
    if os.name == 'nt':
        import ctypes
        
        class CONSOLE_CURSOR_INFO(ctypes.Structure):
            _fields_ = [("dwSize", ctypes.c_int),
                        ("bVisible", ctypes.c_bool)]

        try:
            STD_OUTPUT_HANDLE = -11
            hStdOut = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
            cursorInfo = CONSOLE_CURSOR_INFO()
            ctypes.windll.kernel32.GetConsoleCursorInfo(hStdOut, ctypes.byref(cursorInfo))
            cursorInfo.bVisible = visible
            ctypes.windll.kernel32.SetConsoleCursorInfo(hStdOut, ctypes.byref(cursorInfo))
        except:
            pass


