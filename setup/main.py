import sys
import os
import argparse
import subprocess
import time
import math
import colorsys
from prompt_toolkit.shortcuts import radiolist_dialog, checkboxlist_dialog
from prompt_toolkit.styles import Style
from .utils import Colors, countdown_or_wait, set_cursor_visible
from .builds import BuildManager
from .tests import TestRunner
from .deploy import DeployManager
from .installer import InstallerManager

# Ensure src is in path so we can import core modules if needed directly
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))
from core.config import get_app_version

# Custom style to make the selected item very visible since we hid the cursor
custom_style = Style.from_dict({
    # Dialog (Menu Card): Deep Teal background, White text
    'dialog': 'bg:#004d4d fg:#ffffff',
    'dialog.body': 'bg:#004d4d fg:#ffffff',
    
    # Frame: Gold border and label
    'frame.border': 'fg:#ffd700', 
    'dialog frame.label': 'bg:#004d4d fg:#ffd700 bold',
    'dialog shadow': 'bg:#000000',
    
    # List Selection (Cursored item): Light Teal highlight
    'radio-selected': 'bg:#afeeee fg:#000000 bold', 
    'checkbox-selected': 'bg:#afeeee fg:#000000 bold',
    
    # Button Focus: Gold (Distinct from list selection to prevent confusion)
    'button.focused': 'bg:#ffd700 fg:#000000 bold',
    
    # Checkmarks / Indicators
    'radio-checked': 'fg:#ffd700 bold',
    'checkbox-checked': 'fg:#ffd700 bold',
    'radio-unchecked': 'fg:#ffffff',
    'checkbox-unchecked': 'fg:#ffffff',
})

def run_app_hidden_cursor(app):
    """Run prompt_toolkit app with cursor forcefully hidden via monkey-patch."""
    try:
        # Patch output to ignore show_cursor calls
        if hasattr(app.output, 'show_cursor'):
            app.output.show_cursor = lambda: None
    except:
        pass
    
    return app.run()

def main():
    parser = argparse.ArgumentParser(description="Story Lord Build System")
    parser.add_argument("--build", action="store_true", help="Build Directory Executable")
    parser.add_argument("--onefile", action="store_true", help="Build Single-File Executable")
    parser.add_argument("--installer", action="store_true", help="Build Installer")
    parser.add_argument("--build-all", action="store_true", help="Build All Targets")
    
    parser.add_argument("--install", action="store_true", help="Run Installer/Repair")
    parser.add_argument("--repair", action="store_true", help="Run Repair (Alias for Install)")
    parser.add_argument("--uninstall", action="store_true", help="Run Uninstall")
    
    parser.add_argument("--deploy", action="store_true", help="Run Deployment")
    parser.add_argument("--test", action="store_true", help="Run All Tests")
    
    args, unknown = parser.parse_known_args()
    
    builder = BuildManager()
    tester = TestRunner()
    deployer = DeployManager()
    installer = InstallerManager()
    
    if args.build:
        builder.prepare_build_version()
        builder.run_pyinstaller()
        return
    if args.onefile:
        builder.prepare_build_version()
        builder.run_pyinstaller_onefile()
        return
    if args.installer:
        builder.prepare_build_version()
        builder.run_inno_setup()
        return
    if args.build_all:
        builder.prepare_build_version()
        builder.run_pyinstaller()
        builder.run_pyinstaller_onefile()
        builder.run_inno_setup()
        return
        
    if args.deploy:
        deployer.deploy_release(get_app_version())
        return
    if args.install or args.repair:
        installer.install_app()
        return
    if args.uninstall:
        installer.uninstall_app()
        return
    if args.test:
        tester.run_tests()
        return

    # TUI Mode
    os.system('') # Init ANSI
    set_cursor_visible(False)
    try:
        while True:
            try:
                choice = run_app_hidden_cursor(radiolist_dialog(
                    title="Story Lord System Manager",
                    text="Select Task:",
                    style=custom_style,
                    values=[
                        ("build", "Dev: Build & Test Menu..."),
                        ("deploy", "Dev: Deploy / Release (GitHub)"),
                        ("run_installer", "User: Run Installer (Install / Repair)"),
                        ("exit", "Exit")
                    ]
                ))
                set_cursor_visible(False)
            except Exception as e:
                import traceback
                traceback.print_exc()
                set_cursor_visible(True)
                input("Press Enter to exit...")
                set_cursor_visible(False)
                sys.exit(0)

            if not choice or choice == "exit":
                break

            if choice == "build":
                 # Submenu: Build All vs Custom vs Tests
                build_mode = run_app_hidden_cursor(radiolist_dialog(
                    title="Build & Test Menu",
                    text="Select Action:",
                    style=custom_style,
                    values=[
                        ("all", "Build All (Directory, Portable, Installer)"),
                        ("custom", "Customize Build..."),
                        ("nuke", "Nuke Binaries (Clean bin/)"),
                        ("tests", "Run Tests (Unit Tests)"),
                        ("all_tests", "Run All Tests (Autodiscover)")
                    ]
                ))
                set_cursor_visible(False)
                
                if not build_mode: continue
                
                if build_mode == "tests":
                     discovered = tester.discover_tests()
                     if not discovered:
                         print("No tests found.")
                         set_cursor_visible(True)
                         input("Enter...")
                         set_cursor_visible(False)
                         continue
                     test_values = [(path, os.path.basename(path)) for path in discovered]
                     selected = run_app_hidden_cursor(checkboxlist_dialog(
                        title="Select Tests", values=test_values, style=custom_style
                     ))
                     set_cursor_visible(False)
                     if selected: tester.run_tests(selected)
                
                elif build_mode == "all_tests":
                    tester.run_tests()

                elif build_mode == "all":
                     builder.prepare_build_version()
                     builder.run_pyinstaller()
                     builder.run_pyinstaller_onefile()
                     builder.run_inno_setup()
                
                elif build_mode == "custom":
                    build_choices = run_app_hidden_cursor(checkboxlist_dialog(
                        title="Customize Build",
                        style=custom_style,
                        values=[
                            ("exe", "Build Directory Exe"),
                            ("onefile", "Build Single-File Exe"),
                            ("installer", "Build Installer")
                        ]
                    ))
                    set_cursor_visible(False)
                    if build_choices:
                        builder.prepare_build_version()
                        if "exe" in build_choices: builder.run_pyinstaller()
                        if "onefile" in build_choices: builder.run_pyinstaller_onefile()
                        if "installer" in build_choices: builder.run_inno_setup()

                elif build_mode == "nuke":
                    nuke_choice = run_app_hidden_cursor(radiolist_dialog(
                        title="Confirm Nuke",
                        text="Are you sure you want to delete ALL files in bin/?\nThis cannot be undone.",
                        style=custom_style,
                        values=[("yes", "Yes, Nuke It"), ("no", "Cancel")]
                    ))
                    set_cursor_visible(False)
                    if nuke_choice == "yes":
                        print("Nuking bin/ directory...")
                        import shutil
                        bin_dir = os.path.abspath("bin")
                        if os.path.exists(bin_dir):
                            for filename in os.listdir(bin_dir):
                                file_path = os.path.join(bin_dir, filename)
                                try:
                                    if os.path.isfile(file_path) or os.path.islink(file_path):
                                        os.unlink(file_path)
                                    elif os.path.isdir(file_path):
                                        shutil.rmtree(file_path)
                                except Exception as e:
                                    print(f"Failed to delete {file_path}. Reason: {e}")
                        print("Binaries Nuked.")
                        countdown_or_wait(True, 5)
                        
            elif choice == "deploy":
                 d_choice = run_app_hidden_cursor(radiolist_dialog(
                    title="Deploy Menu",
                    style=custom_style,
                    values=[
                        ("pr", "Submit Pull Request"),
                        ("release", "Deploy Release")
                    ]
                 ))
                 set_cursor_visible(False)
                 
                 if d_choice == "pr":
                     deployer.submit_pull_request(get_app_version())
                 elif d_choice == "release":
                     deployer.deploy_release(get_app_version())

            elif choice == "run_installer":
                installer.install_app()
    finally:
        set_cursor_visible(True)

if __name__ == "__main__":
    main()
