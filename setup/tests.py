import os
import sys
import subprocess
from .utils import Colors, countdown_or_wait

class TestRunner:
    def run_tests(self, specific_files=None):
        print(f"\n{Colors.CYAN}--- Running Unit Tests ---{Colors.ENDC}")
        cmd = [sys.executable, "-m", "unittest"]
        if specific_files:
            cmd.extend(["-v"])
            cmd.extend(specific_files)
        else:
            cmd.extend(["discover", "tests"])
            
        try:
            exit_code = subprocess.call(cmd)
            success = (exit_code == 0)
        except Exception as e:
            print(f"Test Execution Failed: {e}")
            success = False
            
        if not success:
             print(f"\n{Colors.FAIL}Tests Failed!{Colors.ENDC}")
        else:
             print(f"\n{Colors.GREEN}All Tests Passed!{Colors.ENDC}")
             
        countdown_or_wait(success, seconds=2)

    def discover_tests(self):
        test_dir = "tests"
        if not os.path.exists(test_dir):
            return []
        files = [f for f in os.listdir(test_dir) if f.startswith("test_") and f.endswith(".py")]
        return [os.path.join(test_dir, f) for f in files]
