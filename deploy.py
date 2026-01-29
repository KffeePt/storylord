
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
        # Update src/core/_version.py
        try:
            version_file = os.path.join("src", "core", "_version.py")
            with open(version_file, "w") as f:
                f.write("# Auto-generated version file\n")
                f.write(f'__version__ = "{new_version}"\n')
            
            print(f"Updated {version_file} to {new_version}")
            current_version = new_version
        except Exception as e:
            print(f"Failed to update _version.py: {e}")
            pass 

    # 1. Git Commit Logic (Before Release/Tagging)
    # Check for uncommitted changes
    try:
        status_output = subprocess.check_output(["git", "status", "--porcelain"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
        if status_output:
            print("\n[!] Uncommitted changes detected (including version config update if any).")
            commit_choice = input("Commit changes before releasing? (Y/n): ").strip().lower()
            if commit_choice != 'n':
                default_msg = f"chore: Release {current_version}"
                commit_msg = input(f"Enter Commit Message [Default: '{default_msg}']: ").strip()
                if not commit_msg:
                    commit_msg = default_msg
                
                print("Committing changes...")
                subprocess.check_call(["git", "add", "."])
                subprocess.check_call(["git", "commit", "-m", commit_msg])
                
                print("Pushing to origin...")
                subprocess.check_call(["git", "push", "origin", "main"]) # Assuming main
        else:
             print("No uncommitted changes.")
    except Exception as e:
        print(f"Git status check check/commit failed: {e}")
        # Don't return, allow user to decide? Or return?
        # If git fails here, tagging might also fail.
        # But let's proceed to allow manual handling if needed.
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

    # REMOTE BUILD (Default/Only Mode)
    print("\n--- Triggering Remote Build ---")
    print(f"This will push tag {current_version} to GitHub.")
    print("GitHub Actions will automatically build and release the artifacts.")
    
    confirm = input("Proceed? (Y/n): ").strip().lower()
    if confirm == 'n':
        print("Aborted.")
        return

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

