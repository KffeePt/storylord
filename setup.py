import sys
import os
import subprocess
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import radiolist_dialog

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
        result = radiolist_dialog(
            title="Story Lord Build System",
            text="Select a build task:",
            values=[
                ("exe", "Build Executable (PyInstaller)"),
                ("installer", "Build Installer (Inno Setup)"),
                ("exit", "Exit")
            ]
        ).run()

        if result == "exe":
            run_pyinstaller()
        elif result == "installer":
            run_inno_setup()
        else:
            break

if __name__ == "__main__":
    main()
