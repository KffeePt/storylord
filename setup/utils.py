import os
import sys
import time

# Constants
DIST_DIR = os.path.abspath("bin/Dist/StoryLord") 
INSTALLER_DIR = os.path.abspath("bin/Installer")
IS_CI = os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("CI") == "true"

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

    if success:
        print(f"\nSuccess! Continuing in {seconds} seconds...", end="", flush=True)
        for i in range(seconds, 0, -1):
            time.sleep(1)
        print("\n")
    else:
        if IS_CI:
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

def validate_version_basic(version_str: str) -> bool:
    """Strictly validates x.y.z format (digits and dots only)."""
    import re
    return bool(re.match(r"^\d+\.\d+\.\d+$", version_str))

def prompt_version_stage(current_stage: str = "") -> str:
    """Prompts for release stage: a (alpha), b (beta), p (prod), or Enter for current."""
    if IS_CI:
        return current_stage

    stage_display = current_stage.lstrip('_') if current_stage else "prod"
    print(f"\nRelease Stage: {Colors.CYAN}a{Colors.ENDC} (alpha), {Colors.CYAN}b{Colors.ENDC} (beta), {Colors.CYAN}p{Colors.ENDC} (prod), or {Colors.BOLD}Enter{Colors.ENDC} for [{stage_display}]")
    
    set_cursor_visible(True)
    choice = input("Stage: ").strip().lower()
    set_cursor_visible(False)
    
    if choice == 'a' or choice == 'alpha':
        return "_alpha"
    elif choice == 'b' or choice == 'beta':
        return "_beta"
    elif choice == 'p' or choice == 'prod' or choice == 'production':
        return ""
    elif not choice:
        return current_stage
    return current_stage

def get_full_version(base_version: str, stage: str) -> str:
    """Constructs final version string like v1.2.3_alpha."""
    prefix = "" if base_version.startswith("v") else "v"
    return f"{prefix}{base_version}{stage}"



