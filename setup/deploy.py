import os
import subprocess
import time
import shutil
from .utils import Colors, get_latest_local_tag, set_cursor_visible, validate_version_basic, prompt_version_stage, get_full_version, IS_CI

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
            if IS_CI:
                print(f"{Colors.FAIL}[CI] Branching from main is not supported headlessly.{Colors.ENDC}")
                return

            print(f"{Colors.WARNING}[!] You are currently on the 'main' branch.{Colors.ENDC}")
            print("    You typically cannot push directly to main without write access.")
            print(f"{Colors.BOLD}    You should create a feature branch.{Colors.ENDC}")
            
            set_cursor_visible(True)
            branch_name = input(f"Enter new branch name (e.g., {Colors.GREEN}feat/add-login{Colors.ENDC}): ").strip()
            set_cursor_visible(False)
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
                if IS_CI:
                    print(f"{Colors.FAIL}[CI] Uncommitted changes detected. Aborting PR.{Colors.ENDC}")
                    return

                print(f"\n{Colors.WARNING}Uncommitted changes detected.{Colors.ENDC}")
                set_cursor_visible(True)
                commit_msg = input("Enter Commit Message: ").strip()
                set_cursor_visible(False)
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
            set_cursor_visible(True)
            try_anyway = input("Try specific deploy anyway? (y/N): ").strip().lower() == 'y'
            set_cursor_visible(False)
            if not try_anyway:
                return
        # Strip v and labels for the numerical prompt
        current_base = current_version.lstrip('v').split('_')[0]
        
        base_version = current_base
        if not IS_CI:
            while True:
                set_cursor_visible(True)
                tag_input = input(f"Enter Tag Version [v{current_base}] (e.g. 0.5.0): ").strip()
                set_cursor_visible(False)
                
                if not tag_input:
                    base_version = current_base
                    break
                
                # Clean 'v' and validate
                base_version = tag_input.lstrip('v')
                if validate_version_basic(base_version):
                    break
                else:
                    print(f"{Colors.FAIL}Invalid format! Please use numbers and periods (e.g., 0.1.2){Colors.ENDC}")

        # Get stage and construct final tag
        current_parts = current_version.split('_', 1)
        current_stage = f"_{current_parts[1]}" if len(current_parts) > 1 else ""
        
        stage = prompt_version_stage(current_stage)
        tag_version = get_full_version(base_version, stage)
        
        if tag_version:
            try:
                version_file = os.path.join("src", "core", "_version.py")
                with open(version_file, "w") as f:
                    f.write(f'__version__ = "{tag_version}"\n')
                print(f"{Colors.GREEN}Updated {version_file} to {tag_version}{Colors.ENDC}")
                current_version = tag_version
            except Exception as e:
                print(f"{Colors.FAIL}Failed to update _version.py: {e}{Colors.ENDC}")

        try:
            status_output = subprocess.check_output(["git", "status", "--porcelain"], stderr=subprocess.DEVNULL).decode("utf-8").strip()
            if status_output:
                set_cursor_visible(True)
                do_commit = input("Commit changes before releasing? (Y/n): ").strip().lower() != 'n'
                set_cursor_visible(False)
                if do_commit:
                    subprocess.check_call(["git", "add", "."])
                    set_cursor_visible(True)
                    msg = input(f"Commit Message [Release {current_version}]: ").strip() or f"chore: Release {current_version}"
                    set_cursor_visible(False)
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
            set_cursor_visible(True)
            choice = input(f"Overwrite release and force re-trigger CI? ({Colors.GREEN}Y{Colors.ENDC}/n): ").strip().lower()
            set_cursor_visible(False)
            if choice != 'n':
                should_proceed = True
                force_retrigger = True
            else:
                return

        elif remote_tag_exists:
            print(f"\n{Colors.WARNING}[!] Tag {current_version} exists on remote (but no release found).{Colors.ENDC}")
            set_cursor_visible(True)
            choice = input(f"Force re-trigger CI? ({Colors.GREEN}Y{Colors.ENDC}/n): ").strip().lower()
            set_cursor_visible(False)
            if choice != 'n':
                should_proceed = True
                force_retrigger = True
            else:
                return
                
        elif release_exists:
             print(f"{Colors.WARNING}WARNING: Release {current_version} check failed consistency.{Colors.ENDC}")
             set_cursor_visible(True)
             overwrite = input(f"Overwrite release? ({Colors.GREEN}Y{Colors.ENDC}/n): ").strip().lower() != 'n'
             set_cursor_visible(False)
             if overwrite:
                 should_proceed = True
             else:
                 return

        else:
            print(f"Pushing tag {Colors.BLUE}{current_version}{Colors.ENDC} to GitHub.")
            set_cursor_visible(True)
            proceed = input(f"Proceed? ({Colors.GREEN}Y{Colors.ENDC}/n): ").strip().lower() != 'n'
            set_cursor_visible(False)
            if proceed:
                should_proceed = True
            else:
                return

        if not should_proceed and not IS_CI:
            return
        
        if IS_CI: should_proceed = True # Force in CI if triggered

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
