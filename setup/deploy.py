import os
import subprocess
import time
import shutil
from .utils import Colors, get_latest_local_tag, set_cursor_visible

def tag_exists_remote(tag_name):
    try:
        output = subprocess.check_output(
            ["git", "ls-remote", "--tags", "origin", tag_name],
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
        return bool(output)
    except:
        return False

def can_push_to_main():
    try:
        output = subprocess.check_output(
            ["gh", "repo", "view", "--json", "viewerPermission", "--jq", ".viewerPermission"],
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
        return output in ["WRITE", "ADMIN", "MAINTAIN"]
    except:
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

class DeployManager:
    def submit_pull_request(self, current_version):
        print(f"\n{Colors.CYAN}--- Submit Pull Request ---{Colors.ENDC}")
        
        if check_branch_is_main():
            print(f"{Colors.WARNING}[!] You are currently on the 'main' branch.{Colors.ENDC}")
            print("    You typically cannot push directly to main without write access.")
            print(f"{Colors.BOLD}    You should create a feature branch.{Colors.ENDC}")
            
            branch_name = input(f"Enter new branch name (e.g., {Colors.GREEN}feat/add-login{Colors.ENDC}): ").strip()
            if not branch_name:
                print(f"{Colors.FAIL}Aborted. Branch name required.{Colors.ENDC}")
                return

            try:
                subprocess.check_call(["git", "checkout", "-b", branch_name])
                print(f"{Colors.GREEN}Switched to new branch '{branch_name}'{Colors.ENDC}")
            except Exception as e:
                print(f"{Colors.FAIL}Failed to create branch: {e}{Colors.ENDC}")
                return
        
        try:
            status_output = subprocess.check_output(["git", "status", "--porcelain"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
            if status_output:
                print(f"\n{Colors.WARNING}Uncommitted changes detected.{Colors.ENDC}")
                commit_msg = input("Enter Commit Message: ").strip()
                if not commit_msg:
                    print(f"{Colors.FAIL}Aborted. Commit message required.{Colors.ENDC}")
                    return
                
                print("Committing changes...")
                subprocess.check_call(["git", "add", "."])
                subprocess.check_call(["git", "commit", "-m", commit_msg])
            else:
                print(f"{Colors.GREEN}No new changes to commit. Proceeding...{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}Git operations failed: {e}{Colors.ENDC}")
            return

        current_branch = subprocess.check_output(["git", "branch", "--show-current"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
        print(f"Pushing branch '{current_branch}' to origin...")
        try:
            subprocess.check_call(["git", "push", "-u", "origin", current_branch])
        except Exception as e:
            print(f"{Colors.FAIL}Push failed: {e}{Colors.ENDC}")
            return

        print(f"\n{Colors.BLUE}Creating Pull Request via GitHub CLI...{Colors.ENDC}")
        try:
            subprocess.check_call(["gh", "pr", "create"])
            print(f"\n{Colors.GREEN}Successfully opened Pull Request!{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}Failed to create PR: {e}{Colors.ENDC}")

    def deploy_release(self, current_version):
        print(f"\n{Colors.CYAN}--- Deploy Release (Maintainers) ---{Colors.ENDC}")
        
        gh_installed = shutil.which("gh") is not None
        
        if not can_push_to_main():
            print(f"{Colors.FAIL}[!] You do not appear to have WRITE access.{Colors.ENDC}")
            if input("Try specific deploy anyway? (y/N): ").strip().lower() != 'y':
                return

        print(f"\nFormat: x.y.z (Example: {Colors.GREEN}0.2.1{Colors.ENDC})")
        default_tag = get_latest_local_tag()
        prompt_msg = f"Enter Tag Version"
        if default_tag:
            prompt_msg += f" [{default_tag}]"
        prompt_msg += ": "
        
        set_cursor_visible(True)
        tag_input = input(prompt_msg).strip()
        set_cursor_visible(False)
        
        if not tag_input and default_tag:
            tag_input = default_tag
            print(f"Using default: {tag_input}")
        
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
                    f.write(f'__version__ = "{new_version}"\n')
                print(f"{Colors.GREEN}Updated {version_file} to {new_version}{Colors.ENDC}")
                current_version = new_version
            except Exception as e:
                print(f"{Colors.FAIL}Failed to update _version.py: {e}{Colors.ENDC}")

        try:
            status_output = subprocess.check_output(["git", "status", "--porcelain"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
            if status_output:
                if input("Commit changes before releasing? (Y/n): ").strip().lower() != 'n':
                    subprocess.check_call(["git", "add", "."])
                    msg = input(f"Commit Message [Release {current_version}]: ").strip() or f"chore: Release {current_version}"
                    subprocess.check_call(["git", "commit", "-m", msg])
                    subprocess.check_call(["git", "push", "origin", "main"])
        except Exception as e:
            print(f"{Colors.FAIL}Git commit failed: {e}{Colors.ENDC}")

        # Unified Prompt Logic (Copied from existing deploy.py)
        release_exists = False
        if gh_installed:
            try:
                subprocess.check_call(["gh", "release", "view", current_version], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                release_exists = True
            except:
                pass

        print("Checking remote tag status...")
        remote_tag_exists = tag_exists_remote(current_version)
        
        should_proceed = False
        force_retrigger = False
        
        print(f"\n{Colors.CYAN}--- Triggering Remote Build ---{Colors.ENDC}")
        
        if release_exists and remote_tag_exists:
            print(f"\n{Colors.WARNING}[!] Release AND Tag {current_version} already exist on remote.{Colors.ENDC}")
            choice = input(f"Overwrite release and force re-trigger CI? ({Colors.GREEN}y{Colors.ENDC}/N): ").strip().lower()
            if choice == 'y':
                should_proceed = True
                force_retrigger = True
            else:
                return

        elif remote_tag_exists:
            print(f"\n{Colors.WARNING}[!] Tag {current_version} exists on remote (but no release found).{Colors.ENDC}")
            choice = input(f"Force re-trigger CI? ({Colors.GREEN}y{Colors.ENDC}/N): ").strip().lower()
            if choice == 'y':
                should_proceed = True
                force_retrigger = True
            else:
                return
                
        elif release_exists:
             print(f"{Colors.WARNING}WARNING: Release {current_version} check failed consistency.{Colors.ENDC}")
             if input(f"Overwrite release? ({Colors.GREEN}y{Colors.ENDC}/N): ").strip().lower() == 'y':
                 should_proceed = True
             else:
                 return

        else:
            print(f"Pushing tag {Colors.BLUE}{current_version}{Colors.ENDC} to GitHub.")
            if input(f"Proceed? ({Colors.GREEN}Y{Colors.ENDC}/n): ").strip().lower() != 'n':
                should_proceed = True
            else:
                return

        if not should_proceed:
            return

        if force_retrigger:
            print(f"{Colors.WARNING}Deleting remote tag...{Colors.ENDC}")
            try:
                subprocess.check_call(["git", "push", "--delete", "origin", current_version])
                time.sleep(2)
            except:
                pass
             
        # Create/Push Tag
        try:
             subprocess.check_call(["git", "tag", current_version])
        except: pass
             
        try:
            subprocess.check_call(["git", "push", "origin", current_version])
            print(f"{Colors.GREEN}Tag pushed successfully!{Colors.ENDC}")
            print(f"View progress at: {Colors.UNDERLINE}https://github.com/KffeePt/storylord/actions{Colors.ENDC}")
        except Exception as e:
            print(f"{Colors.FAIL}Failed to push tag: {e}{Colors.ENDC}")
