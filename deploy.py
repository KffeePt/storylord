
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

def tag_exists_remote(tag_name):
    """Check if a tag exists on the remote origin."""
    try:
        output = subprocess.check_output(
            ["git", "ls-remote", "--tags", "origin", tag_name],
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
        return bool(output)
    except:
        return False

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


def can_push_to_main():
    """Check if the user has WRITE or ADMIN permissions."""
    try:
        # Check permissions using gh
        output = subprocess.check_output(
            ["gh", "repo", "view", "--json", "viewerPermission", "--jq", ".viewerPermission"],
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
        # WRITE, ADMIN, MAINTAIN are typically allowed to push to main
        return output in ["WRITE", "ADMIN", "MAINTAIN"]
    except:
        # Fallback: assume False if gh checks fail to ensure safety
        return False

def check_branch_is_main():
    try:
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"], 
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
        return branch == "main" or branch == "master"
    except:
        return False

def submit_pull_request(current_version):
    print("\n--- Submit Pull Request ---")
    
    # 1. Branch Check
    if check_branch_is_main():
        print("[!] You are currently on the 'main' branch.")
        print("    You typically cannot push directly to main without write access.")
        print("    You should create a feature branch.")
        
        branch_name = input("Enter new branch name (e.g., feat/add-login): ").strip()
        if not branch_name:
            print("Aborted. Branch name required.")
            return

        try:
            subprocess.check_call(["git", "checkout", "-b", branch_name])
            print(f"Switched to new branch '{branch_name}'")
        except Exception as e:
            print(f"Failed to create branch: {e}")
            return
    
    # 2. Commit Logic
    try:
        status_output = subprocess.check_output(["git", "status", "--porcelain"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
        if status_output:
            print("\nUncommitted changes detected.")
            commit_msg = input("Enter Commit Message: ").strip()
            if not commit_msg:
                print("Aborted. Commit message required.")
                return
            
            print("Committing changes...")
            subprocess.check_call(["git", "add", "."])
            subprocess.check_call(["git", "commit", "-m", commit_msg])
        else:
            print("No new changes to commit. Proceeding with existing commits...")
    except Exception as e:
        print(f"Git operations failed: {e}")
        return

    # 3. Push Branch
    current_branch = subprocess.check_output(["git", "branch", "--show-current"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
    print(f"Pushing branch '{current_branch}' to origin...")
    try:
        subprocess.check_call(["git", "push", "-u", "origin", current_branch])
    except Exception as e:
        print(f"Push failed: {e}")
        return

    # 4. Create PR
    print("\nCreating Pull Request via GitHub CLI...")
    try:
        # Interactive mode is best for PRs (title/body)
        subprocess.check_call(["gh", "pr", "create"])
        print("\nSuccessfully opened Pull Request!")
    except Exception as e:
        print(f"Failed to create PR: {e}")
        print("You can manually create it at: https://github.com/KffeePt/storylord/pulls")

def deploy_release(current_version, gh_installed):
    print("\n--- Deploy Release (Maintainers) ---")
    
    # Permission Guard
    if not can_push_to_main():
        print("[!] You do not appear to have WRITE access to this repository.")
        print("    You likely cannot push tags or merge to main.")
        print("    Please use 'Submit Pull Request' instead.")
        choice = input("Try specific deploy anyway? (y/N): ").strip().lower()
        if choice != 'y':
            return

    # Update version logic
    print("\nFormat: x.y.z (Example: 0.2.1)")
    tag_input = input(f"Enter Tag Version v: ").strip()
    
    new_version = ""
    if tag_input:
        if not tag_input.lower().startswith("v"):
            new_version = f"v{tag_input}"
        else:
            new_version = tag_input
    
    if new_version:
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

    # Commit Logic
    try:
        status_output = subprocess.check_output(["git", "status", "--porcelain"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
        if status_output:
            print("\n[!] Uncommitted changes detected.")
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
                subprocess.check_call(["git", "push", "origin", "main"])
        else:
             print("No uncommitted changes.")
    except Exception as e:
        print(f"Git check/commit failed: {e}")
        pass

    # Existing Release Check
    if gh_installed:
        try:
            subprocess.check_call(["gh", "release", "view", current_version], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"WARNING: Release {current_version} already exists!")
            if input("Overwrite? (y/N): ").strip().lower() != 'y':
                return
        except:
            pass

    # Remote Build Trigger
    print("\n--- Triggering Remote Build ---")
    if input("Proceed? (Y/n): ").strip().lower() == 'n':
        print("Aborted.")
        return

    # Tag & Push (With Remote Check)
    print("Ensuring Git Tag exists...")
    remote_tag_exists = tag_exists_remote(current_version)
    tag_exists = False
    try:
         subprocess.check_call(["git", "rev-parse", current_version], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
         tag_exists = True
    except:
         pass
         
    if remote_tag_exists:
        print(f"\n[!] Tag {current_version} ALREADY EXISTS on remote.")
        print("    Pushing again does nothing (no CI trigger).")
        retrigger = input("Force re-trigger CI? (Delete remote tag & re-push) (Y/n): ").strip().lower()
        if retrigger != 'n':
            print("Deleting remote tag...")
            try:
                subprocess.check_call(["git", "push", "--delete", "origin", current_version])
                time.sleep(2)
            except Exception as e:
                print(f"Warning: Failed to delete remote tag: {e}")
        else:
            print("Keeping existing remote tag.")
         
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
    
    print("\nDone. Window closing in 15s...")
    time.sleep(15)

def main_menu():
    print("--- Story Lord Dev Tools ---")
    current_version = get_app_version()
    print(f"Current Version: {current_version}")
    
    gh_installed = shutil.which("gh") is not None
    if not gh_installed:
        print("Warning: 'gh' CLI not found. Some features will be limited.")
    
    # Check permissions once
    has_write_access = False
    if gh_installed:
        print("Checking GitHub permissions...")
        has_write_access = can_push_to_main()
    
    while True:
        print("\nSelect Option:")
        print("1. Submit Pull Request (For Contributors)")
        print("2. Deploy Release (For Maintainers)")
        print("3. Exit")
        
        choice = input("\nChoice (1-3): ").strip()
        
        if choice == '1':
            submit_pull_request(current_version)
        elif choice == '2':
            if not has_write_access:
                print("\n[!] WARNING: You do not appear to have write access.")
            deploy_release(current_version, gh_installed)
        elif choice == '3':
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nCancelled.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"\nFATAL ERROR: {e}")
    finally:
        print("\nExiting...")
        time.sleep(1)

