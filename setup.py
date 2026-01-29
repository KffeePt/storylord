import sys
import os
import subprocess
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import checkboxlist_dialog

def run_pyinstaller():
    print("Building Executable with PyInstaller...")
    try:
        # Run Pyinstaller
        subprocess.check_call([
            "pyinstaller", 
            "--clean",
            "--noconfirm",
            "story_lord.spec"
        ])
        print("Build Complete! Check bin/Release (mapped in spec).")
    except Exception as e:
        print(f"Build Failed: {e}")
        input("Press Enter...")

def run_inno_setup():
    print("Building Installer with Inno Setup...")
    try:
        # Require ISCC in path
        subprocess.check_call(["iscc", "installer.iss"])
        print("Installer Complete! Check bin/Installer.")
    except FileNotFoundError:
        print("Error: 'iscc' not found. Ensure Inno Setup is in your PATH.")
        input("Press Enter...")
    except Exception as e:
        print(f"Installer Build Failed: {e}")
        input("Press Enter...")

def main():
    while True:
        results = checkboxlist_dialog(
            title="Story Lord Build System",
            text="Select build tasks (Space to select, Enter to run):",
            values=[
                ("exe", "Build Executable (PyInstaller)"),
                ("installer", "Build Installer (Inno Setup)")
            ]
        ).run()

        if not results:
            break
            
        for task in results:
            if task == "exe":
                run_pyinstaller()
            elif task == "installer":
                run_inno_setup()
        
        break

if __name__ == "__main__":
    main()
