import sys
import os
import subprocess
import hashlib
import json
import shutil
from pathlib import Path

# Ensure src is in path so we can import core modules
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import checkboxlist_dialog, radiolist_dialog, message_dialog, yes_no_dialog

# Constants
# Redirect PyInstaller output to bin/Portable (was bin/Dist)
DIST_DIR = os.path.abspath("bin/Portable/StoryLord") 
INSTALLER_DIR = os.path.abspath("bin/Installer")
DEFAULT_INSTALL_PATH = os.path.expandvars(r"%ProgramFiles%\Story Lord")
CONFIG_DIR = os.path.expanduser("~/.storylord")
STORIES_DIR = os.path.expanduser("~/Documents/StoryLord")

class BuildSystem:
    def __init__(self):
        pass
        
    def get_file_hash(self, path):
        sha256_hash = hashlib.sha256()
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def generate_manifest(self):
        print("Generating Manifest...")
        manifest = {}
        base_len = len(DIST_DIR) + 1
        
        for root, dirs, files in os.walk(DIST_DIR):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = full_path[base_len:] 
                try:
                    h = self.get_file_hash(full_path)
                    manifest[rel_path] = h
                except Exception as e:
                    print(f"Error hashing {rel_path}: {e}")
                    
        manifest_path = os.path.join(DIST_DIR, "manifest.json")
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"Manifest saved to {manifest_path}")

    def _countdown_or_wait(self, success: bool, seconds: int = 5):
        """On success: auto-continue after countdown. On failure: wait for Enter."""
        import time
        # Check if running in a non-interactive environment (e.g., GitHub Actions)
        is_ci = os.environ.get("GITHUB_ACTIONS") == "true" or os.environ.get("CI") == "true"

        if success:
            print(f"\nSuccess! Continuing in {seconds} seconds...", end="", flush=True)
            for i in range(seconds, 0, -1):
                # print(f"{i}...", end="", flush=True) # cleaner to just wait or simple dots
                time.sleep(1)
            print("\n")
        else:
            if is_ci:
                print("\n[CI DETECTED] Build Failed. Exiting immediately without waiting for input.")
                sys.exit(1)
            else:
                input("\nPress Enter to continue...")

    def run_pyinstaller(self):
        print("Building Directory Executable with PyInstaller...")
        success = False
        try:
            # Output to bin/Portable/StoryLord
            # --distpath sets the parent of the output folder.
            dist_path = os.path.abspath("bin/Portable")
            work_path = os.path.abspath("bin/Build")
            
            subprocess.check_call([
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                "--distpath", dist_path,
                "--workpath", work_path,
                "story_lord.spec"
            ])
            self.generate_manifest()
            print(f"Build Complete! Check {DIST_DIR}.")
            success = True
        except Exception as e:
            print(f"Build Failed: {e}")
            success = False
        
        self._countdown_or_wait(success)

    def _find_iscc(self):
        # Check PATH first
        if shutil.which("iscc"):
            return "iscc"
            
        # Check Standard Locations
        prog_files = [os.environ.get("ProgramFiles", "C:\\Program Files"), os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")]
        for pf in prog_files:
            if not pf: continue
            # Try Inno Setup 6, 5, etc.
            for v in ["Inno Setup 6", "Inno Setup 5", "Inno Setup"]:
                candidate = os.path.join(pf, v, "ISCC.exe")
                if os.path.exists(candidate):
                    return candidate
        return None

    def run_pyinstaller_onefile(self):
        print("Building Single-File Executable with PyInstaller...")
        success = False
        try:
            # Output to bin/Release (or similar, user said "deploy to a single StoryLord.exe")
            # Let's put it in bin/Release for clarity compared to bin/Dist (directory)
            dist_path = os.path.abspath("bin/Release")
            work_path = os.path.abspath("bin/BuildOneFile")
            
            subprocess.check_call([
                sys.executable, "-m", "PyInstaller",
                "--clean",
                "--noconfirm",
                # "--onefile", # Removed: Spec file handles this
                "--distpath", dist_path,
                "--workpath", work_path,
                "story_lord_onefile.spec"
            ])
            
            # Rename to StoryLord-Portable.exe to distinguish
            src = os.path.join(dist_path, "StoryLord.exe")
            dst = os.path.join(dist_path, "StoryLord-Portable.exe")
            if os.path.exists(src):
                if os.path.exists(dst): os.remove(dst)
                os.rename(src, dst)
                print(f"Renamed to {dst}")
                
            print(f"OneFile Build Complete! Check {dist_path}.")
            success = True
        except Exception as e:
            print(f"OneFile Build Failed: {e}")
            success = False
        
        self._countdown_or_wait(success)

    def run_inno_setup(self):
        print("Building Installer with Inno Setup...")
        success = False
        try:
            # Check if manifests exists, if not warn
            if not os.path.exists(os.path.join(DIST_DIR, "manifest.json")):
                 print("Warning: manifest.json not found in dist. Repair functionality may be limited.")
            
            iscc_cmd = self._find_iscc()
            if not iscc_cmd:
                 raise FileNotFoundError("ISCC.exe (Inno Setup Compiler) not found in PATH or standard Program Files locations.")
            
            # Get version
            from core.config import get_app_version
            version = get_app_version()
            print(f"Using Version: {version}")
            
            # Pass version to ISCC
            # /DMyAppVersion="v1.0..."
            subprocess.check_call([iscc_cmd, f"/DMyAppVersion={version}", "installer.iss"])
            print("Installer Complete! Check bin/Installer.")
            success = True
        except FileNotFoundError as fnf:
            print(f"Error: {fnf}")
            success = False
        except Exception as e:
            print(f"Installer Build Failed: {e}")
            success = False
        
        self._countdown_or_wait(success)

    def install_app(self):
        installer_path = os.path.join(INSTALLER_DIR, "StoryLordSetup.exe")
        if os.path.exists(installer_path):
            print("Launching Installer...")
            print("The installer will handle Installation, Re-Installation, and Repair/Verification.")
            try:
                subprocess.Popen([installer_path])
            except Exception as e:
                 print(f"Failed to launch: {e}")
        else:
            print("Installer not found. Please Build Installer first.")
            input("Press Enter...")

    def repair_app(self):
        # Redirect to install_app as requested
        self.install_app()

    def uninstall_app(self):
        print("Launching Uninstaller...")
        # LOCATE uninstaller
        unins = os.path.join(DEFAULT_INSTALL_PATH, "unins000.exe")
        
        if not os.path.exists(unins):
                # Try finding it in standard location?
                # or prompt?
                # Just warn.
                print(f"Uninstaller not found at {unins}")
                unins = prompt("Path to unins000.exe (Leave empty to cancel): ", default="").strip()
        
        if unins and os.path.exists(unins):
            subprocess.call([unins])
            print("Uninstaller launched.")
        else:
            print("Uninstaller not found. Please remove Program Files manually.")
        
        # Only pause here if manually run, but good to check success
        self._countdown_or_wait(True)



def main():
    import argparse
    parser = argparse.ArgumentParser(description="Story Lord Build System")
    parser.add_argument("--build", action="store_true", help="Build Directory Executable")
    parser.add_argument("--onefile", action="store_true", help="Build Single-File Executable")
    parser.add_argument("--installer", action="store_true", help="Build Installer")
    parser.add_argument("--install", action="store_true", help="Run Installer/Repair")
    parser.add_argument("--repair", action="store_true", help="Run Repair (Alias for Install)")
    parser.add_argument("--uninstall", action="store_true", help="Run Uninstall")
    
    parser.add_argument("--deploy", action="store_true", help="Run Deployment (Build All + Release)")
    
    args, unknown = parser.parse_known_args()
    
    bs = BuildSystem()
    
    if args.build:
        bs.run_pyinstaller()
        return
    if args.onefile:
        bs.run_pyinstaller_onefile()
        return
    if args.installer:
        bs.run_inno_setup()
        return
    if args.deploy:
        subprocess.call([sys.executable, "deploy.py"])
        return
    if args.install or args.repair:
        bs.install_app()
        return
    if args.uninstall:
        bs.uninstall_app() # Might still prompt
        return

    # TUI Mode
    while True:
        try:
            choice = radiolist_dialog(
                title="Story Lord System Manager",
                text="Select Task:",
                values=[
                    ("build", "Dev: Build... (Select multiple)"),
                    ("deploy", "Dev: Deploy / Release (GitHub)"),
                    ("install", "User: Install / Re-Install / Repair"),
                    ("uninstall", "User: Uninstall"),
                    ("exit", "Exit")
                ]
            ).run()
        except Exception as e:
            print(f"TUI Error (Not a localized terminal?): {e}")
            print("Use command line arguments.")
            sys.exit(1)

        if not choice or choice == "exit":
            break

        if choice == "build":
            # Submenu for multi-select build
            build_choices = checkboxlist_dialog(
                title="Build Menu",
                text="Select items to build (Space to toggle, Enter to confirm):",
                values=[
                    ("exe", "Build Directory Exe (PyInstaller)"),
                    ("onefile", "Build Single-File Exe (PyInstaller)"),
                    ("installer", "Build Installer (Inno Setup)")
                ]
            ).run()
            
            if build_choices:
                if "exe" in build_choices:
                    bs.run_pyinstaller()
                if "onefile" in build_choices:
                    bs.run_pyinstaller_onefile()
                if "installer" in build_choices:
                    bs.run_inno_setup()
                    
        elif choice == "deploy":
             subprocess.call([sys.executable, "deploy.py"])

        elif choice == "install":
            bs.install_app()
        elif choice == "repair":
            bs.repair_app()
        elif choice == "uninstall":
            bs.uninstall_app()

if __name__ == "__main__":
    main()
