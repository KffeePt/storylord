import os
import sys
import signal
import atexit
import time
from pathlib import Path
from core.config import APP_DATA_ROOT

# Lock Directory
LOCK_DIR = os.path.join(APP_DATA_ROOT, "locks")

def get_mode():
    if getattr(sys, 'frozen', False):
        return "RELEASE"
    return "DEBUG"

def get_lock_file(mode):
    return os.path.join(LOCK_DIR, f"{mode}.lock")

def is_pid_running(pid):
    """
    Check if a PID is running using os.kill(pid, 0).
    On Windows, this checks existence.
    """
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def kill_pid(pid):
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(1) # Give it a moment
        if is_pid_running(pid):
            os.kill(pid, signal.SIGTERM) # Force? SIGKILL not always avail on Win via kill?
            # Windows: SIGTERM is mostly kill.
            # Using taskkill might be stronger if needed:
            # os.system(f"taskkill /F /PID {pid}")
    except Exception as e:
        print(f"Error killing process {pid}: {e}")

def resolve_conflict(mode, pid):
    """
    Prompt user to resolve conflict.
    Returns True if solved (process killed), False if user cancels.
    """
    from prompt_toolkit.shortcuts import connect_to_app, yes_no_dialog
    
    # Needs to handle CLI vs TUI environment
    # simplistic input for now if TUI not fully init
    print(f"\n! Another instance of Story Lord ({mode}) is running (PID: {pid}).")
    val = input("Do you want to [K]ill it and proceed, or [C]ancel? (k/c): ").strip().lower()
    
    if val == 'k':
        print(f"Killing PID {pid}...")
        kill_pid(pid)
        return True
    else:
        return False

def ensure_single_instance():
    """
    Enforces single instance per mode (DEBUG/RELEASE).
    """
    if not os.path.exists(LOCK_DIR):
        os.makedirs(LOCK_DIR)
        
    mode = get_mode()
    lock_file = get_lock_file(mode)
    
    # Check Lock
    if os.path.exists(lock_file):
        try:
            with open(lock_file, "r") as f:
                content = f.read().strip()
                if content:
                    old_pid = int(content)
                    if is_pid_running(old_pid):
                        # Conflict
                        if not resolve_conflict(mode, old_pid):
                            print("Startup Cancelled.")
                            sys.exit(0)
                        # If resolved, we proceed (old process dead)
        except ValueError:
            pass # Corrupt lock file, ignore
        except Exception as e:
            print(f"Error checking lock: {e}")
            
    # Acquire Lock
    try:
        pid = os.getpid()
        with open(lock_file, "w") as f:
            f.write(str(pid))
        
        # Register Release
        def release():
            try:
                if os.path.exists(lock_file):
                    # Verify it's US holding it
                    with open(lock_file, "r") as f:
                        if f.read().strip() == str(pid):
                            os.remove(lock_file)
            except:
                pass
                
        atexit.register(release)
        
    except Exception as e:
        print(f"Failed to acquire lock: {e}")
        # Proceed anyway? Or fail? 
        # Fail safe: proceed, but warn.

