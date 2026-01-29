import os
import sys
import subprocess
import urllib.request
from .utils import Colors, INSTALLER_DIR, countdown_or_wait

import glob

DEFAULT_INSTALL_PATH = os.path.expandvars(r"%ProgramFiles%\Story Lord")

class InstallerManager:
    def download_installer(self, target_dir):
        print(f"{Colors.BLUE}Installer NOT found in current directory.{Colors.ENDC}")
        print(f"{Colors.CYAN}Downloading latest installer to: {target_dir}{Colors.ENDC}")
        
        os.makedirs(target_dir, exist_ok=True)
        
        # Try GH CLI first
        try:
            print("Checking via 'gh' CLI...")
            # Pattern match any version
            subprocess.check_call([
                "gh", "release", "download", 
                "--pattern", "StoryLordSetup_*.exe", 
                "--dir", target_dir,
                "--clobber" # Overwrite old ones
            ])
            return True
        except Exception as e:
            print(f"GH CLI download failed: {e}")
            
        # Fallback (Manual URL) - Hard to do with dynamic naming without querying API first.
        # We will rely on GH CLI for now as primary method for updates.
        print(f"{Colors.WARNING}Direct download fallback not fully supported for dynamic versions.{Colors.ENDC}")
        print(f"Please install GitHub CLI or download manually from: https://github.com/KffeePt/storylord/releases/latest")
        return False

    def install_app(self):
        # 1. Check local bin/Installer (Project Build Folder)
        # 2. Check ~/Downloads (Download Folder)
        
        folders_to_check = [
            INSTALLER_DIR, # bin/Installer
            os.path.join(os.path.expanduser("~"), "Downloads")
        ]
        
        pattern = "StoryLordSetup_*.exe"
        fallback = "StoryLordSetup.exe"
        
        installer_path = None
        all_matches = []
        
        for folder in folders_to_check:
            if not os.path.exists(folder): continue
            
            # Look for versioned matches
            matches = glob.glob(os.path.join(folder, pattern))
            all_matches.extend(matches)
            
            # Check for generic fallback (legacy or unversioned local build)
            generic = os.path.join(folder, fallback)
            if os.path.exists(generic):
                # Only add if not already covered (though timestamp selection handles it)
                if generic not in all_matches:
                    all_matches.append(generic)
        
        if all_matches:
            # Pick latest modified among all found
            installer_path = max(all_matches, key=os.path.getctime)
            print(f"Found installer: {os.path.basename(installer_path)} in {os.path.dirname(installer_path)}")
            
            if input("Download fresh version from GitHub anyway? (y/N): ").strip().lower() == 'y':
                installer_path = None # Force download
                
        if not installer_path:
            download_dir = folders_to_check[1] # Downloads
            if self.download_installer(download_dir):
                # Look again in Downloads
                matches = glob.glob(os.path.join(download_dir, pattern))
                if matches:
                    installer_path = max(matches, key=os.path.getctime)
            
        if installer_path and os.path.exists(installer_path):
            print(f"{Colors.CYAN}Launching Installer: {installer_path}{Colors.ENDC}")
            try:
                subprocess.Popen([installer_path])
            except Exception as e:
                 print(f"{Colors.FAIL}Failed to launch: {e}{Colors.ENDC}")
        else:
             print(f"{Colors.FAIL}Installer missing or download failed.{Colors.ENDC}")

    def uninstall_app(self):
        print("Launching Uninstaller...")
        unins = os.path.join(DEFAULT_INSTALL_PATH, "unins000.exe")
        
        if unins and os.path.exists(unins):
            subprocess.call([unins])
        else:
            print(f"{Colors.WARNING}Uninstaller not found at {unins}{Colors.ENDC}")
            print("Please uninstall manually via Windows Settings.")
        
        countdown_or_wait(True)
