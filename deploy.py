
import os
import sys
import subprocess
import shutil
import time

# Ensure src is in path to import core safely
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from core.config import get_app_version, APP_DATA_ROOT
from core.version_manager import VersionManager
from setup import BuildSystem

def print_summary(report):
    print("\n" + "="*40)
    print("       DEPLOYMENT SUMMARY       ")
    print("="*40)
    print(f"{'Step':<25} | {'Status':<10}")
    print("-" * 40)
    for step, status in report.items():
        symbol = "SUCCESS" if status else "FAILED"
        print(f"{step:<25} | {symbol}")
    print("="*40 + "\n")

def main():
    print("--- Story Lord Deployer ---")
    
    # 0. Version Management
    current_version = get_app_version()
    
    # Check if gh is installed
    gh_installed = shutil.which("gh") is not None
    latest_gh_version = "Unknown (gh CLI not found)"
    
    if gh_installed:
        try:
            # gh release list --limit 1 --json tagName --jq ".[0].tagName"
            output = subprocess.check_output(
                ["gh", "release", "list", "--limit", "1", "--json", "tagName", "--jq", ".[0].tagName"],
                stderr=subprocess.DEVNULL
            ).decode("utf-8").strip()
            if output:
                latest_gh_version = output
            else:
                latest_gh_version = "None"
        except:
             latest_gh_version = "Error Fetching"

    print(f"Current System Version: {current_version}")
    print(f"Latest GitHub Version:  {latest_gh_version}")
    

    if not gh_installed:
        print("Warning: GitHub CLI (gh) not found in PATH.")
        print("Please download it from: https://cli.github.com/")
        print("Deployment to GitHub Releases will be SKIPPED.")
        choice = input("Continue with Local Build Only? (Y/n): ").strip().lower()
        if choice == 'n':
            return
    else:
        # Check Auth Status
        print("Checking GitHub Auth Status...")
        try:
            subprocess.check_call(["gh", "auth", "status"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print("You are NOT logged in to GitHub.")
            print("Launching authentication wizard...")
            try:
                # Run interactive auth
                subprocess.check_call(["gh", "auth", "login"])
            except Exception as e:
                print(f"Authentication failed/aborted: {e}")
                return

    # Prompt for version
    # "input the tag version v: [version without the v as it is going to be autonmatically added ]"
    print("\nFormat: x.y.z (Example: 0.2.1)")
    tag_input = input(f"Enter Tag Version v: ").strip()
    
    new_version = ""
    if tag_input:
        # Auto-add v if missing
        if not tag_input.lower().startswith("v"):
            new_version = f"v{tag_input}"
        else:
            new_version = tag_input
    
    if new_version:
        # Update Config
        try:
            config_path = os.path.join(APP_DATA_ROOT, "config", "config.json")
            vm = VersionManager(config_path)
            vm.save_version_to_config(new_version)
            print(f"Version updated to {new_version}")
            current_version = new_version
        except Exception as e:
            print(f"Failed to update version: {e}")
            pass 

    # Check if release exists
    print(f"Checking if release {current_version} exists on GitHub...")
    release_exists = False
    if gh_installed:
        try:
            subprocess.check_call(["gh", "release", "view", current_version], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            release_exists = True
            print(f"WARNING: Release {current_version} already exists!")
            choice = input("Overwrite existing release? (y/N): ").strip().lower()
            if choice != 'y':
                print("Aborted by user.")
                return
        except:
            print(f"Release {current_version} does not exist. Proceeding...")

    # REMOTE VS LOCAL BUILD PROMPT
    print("\n--- Deployment Mode ---")
    print("1. Remote Build (Recommended): Trigger GitHub Actions to build & release.")
    print("2. Local Build: Build on this machine and upload manually.")
    mode = input("Select Mode (1/2) [Default: 1]: ").strip()
    
    if mode == "2":
        # LOCAL BUILD LOGIC FLOW
        pass 
    else:
        # REMOTE BUILD
        print(f"\nTriggering Remote Build for {current_version}...")
        
        # Tag & Push
        print("Ensuring Git Tag exists...")
        tag_exists = False
        try:
             subprocess.check_call(["git", "rev-parse", current_version], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
             tag_exists = True
        except:
             pass
             
        if not tag_exists:
             subprocess.call(["git", "tag", current_version])
             print(f"Created tag {current_version}")
             
        print("Pushing tag to origin...")
        try:
            subprocess.check_call(["git", "push", "origin", current_version])
            print("Tag pushed successfully!")
            print("GitHub Actions should now start the build process.")
            print(f"View progress at: https://github.com/KffeePt/storylord/actions")
        except Exception as e:
             print(f"Failed to push tag: {e}")
             
        print("Finished. Window will close in 15 seconds...")
        time.sleep(15)
        return

    # LOCAL BUILD CONTINUES BELOW...
    # Tag Logic (Redundant check if local flow chosen, but safe to keep)

    # We should ensure the tag exists locally and is pushed
    print("Ensuring Git Tag exists and is pushed...")
    try:
        # Check local tag
        subprocess.check_call(["git", "rev-parse", current_version], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        print(f"Tag {current_version} not found locally.")
        create_tag = input(f"Create tag {current_version} now? (Y/n): ").strip().lower()
        if create_tag != 'n':
             subprocess.call(["git", "tag", current_version])
    
    # Push tag
    print("Pushing tag to origin...")
    try:
        subprocess.call(["git", "push", "origin", current_version])
    except Exception as e:
        print(f"Warning: Failed to push tag: {e}")

    report = {}
    bs = BuildSystem()
    
    # 1. Build OneFile
    print(f"\n[Step 1] Building Single File Executable ({current_version})...")
    try:
        bs.run_pyinstaller_onefile()
        report["Build OneFile"] = True
    except Exception:
        report["Build OneFile"] = False
    
    # 2. Build Installer
    print("\n[Step 2] Building Standard Executable (for Installer)...")
    try:
        # Standard build often needed for installer to bundle content?
        # Setup.py logic implies Installer calls standard build? No, installer.iss usually looks at files.
        # run_pyinstaller builds to bin/Portable.
        bs.run_pyinstaller()
        report["Build Directory"] = True
    except:
         report["Build Directory"] = False

    print("\n[Step 3] Building Installer...")
    try:
        bs.run_inno_setup()
        report["Build Installer"] = True
    except:
        report["Build Installer"] = False
    
    # 3. Locate Artifacts
    onefile = os.path.abspath("bin/Release/StoryLord-Portable.exe")
    installer = os.path.abspath("bin/Installer/StoryLordSetup.exe")
    
    release_ready = True
    if not os.path.exists(onefile):
        print("Error: Single File EXE not found!")
        release_ready = False
    if not os.path.exists(installer):
        print("Error: Installer not found!")
        release_ready = False
        
    # 4. Release via GH CLI
    if release_ready:
        print(f"\n[Step 4] Creating/Updating GitHub Release {current_version}...")
        
        # Create Title "Setup v..."
        title = f"Setup {current_version}"
        
        cmd = ["gh", "release", "create", current_version, onefile, installer, "--title", title, "--generate-notes"]
        
        if release_exists:
            # gh release create fails if exists. Use create/edit or upload?
            # Safer to delete and recreate or just upload?
            # 'gh release create' fails if tag exists? No, only if release exists.
            # If release exists, we use upload --clobber
             print("Release exists. Uploading assets...")
             cmd = ["gh", "release", "upload", current_version, onefile, installer, "--clobber"]

        try:
            subprocess.check_call(cmd)
            report["GitHub Release"] = True
            print("Deployment Complete!")
        except Exception as e:
            report["GitHub Release"] = False
            print(f"Deployment Failed: {e}")
    else:
        report["GitHub Release"] = False
        print("Skipping Release due to missing artifacts.")

    print_summary(report)
        
    print("Finished. Window will close in 15 seconds...")
    time.sleep(15)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nFATAL ERROR: {e}")
    finally:
        print("\nPress Enter to close window...")
        input()

