import os
import sys
import json
import urllib.request
import webbrowser
import platform
import subprocess
from typing import Tuple, Optional

class UpdateChecker:
    REPO_OWNER = "KffeePt"
    REPO_NAME = "storylord"
    API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
    
    def __init__(self):
        pass

    def check_for_update(self, current_version: str) -> Tuple[bool, Optional[str], Optional[dict]]:
        """
        Checks against GitHub Releases.
        Returns (update_available, latest_version_tag, release_data)
        """
        try:
            # Add User-Agent to avoid 403
            req = urllib.request.Request(
                self.API_URL, 
                headers={'User-Agent': 'StoryLord-Updater'}
            )
            
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status != 200:
                    return False, None, None
                
                data = json.loads(response.read().decode('utf-8'))
                latest_tag = data.get("tag_name", "")
                
                # Simple string comparison or semver parse?
                # current: v0.0.1, latest: v0.0.2
                # If strings differ, assume update? 
                # Or use proper parsing. Let's assume strict equality triggers "different", 
                # but we should check if new is actually newer.
                # For now, strict inequality is enough to prompt.
                
                if latest_tag and latest_tag != current_version:
                    return True, latest_tag, data
                    
        except Exception as e:
            print(f"[Updater] Check failed: {e}")
            
        return False, None, None

    def is_installed_mode(self) -> bool:
        """
        Heuristic: If running from 'Program Files', it's installed.
        """
        exe_path = sys.executable
        # Normalize for comparison
        exe_path = os.path.normpath(exe_path).lower()
        
        program_files = os.environ.get("ProgramFiles", "C:\\Program Files").lower()
        program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)").lower()
        
        return program_files in exe_path or program_files_x86 in exe_path

    def download_update(self, release_data: dict, portable: bool = False) -> Optional[str]:
        """
        Downloads the appropriate asset to ~/Downloads.
        Returns path to downloaded file.
        """
        assets = release_data.get("assets", [])
        target_name = "StoryLord-Portable.exe" if portable else "StoryLordSetup.exe"
        
        download_url = None
        for asset in assets:
            if target_name.lower() in asset["name"].lower():
                download_url = asset["browser_download_url"]
                break
        
        if not download_url:
            # Fallback: just open release page
            return None
            
        # Download
        try:
            downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
            target_path = os.path.join(downloads_dir, target_name)
            
            # Streaming download not easily done with urrlib without blocked UI.
            # For simplicity in this iteration, use urllib.urlretrieve (legacy but works) or simple chunked write.
            
            print(f"[Updater] Downloading to {target_path}...")
            with urllib.request.urlopen(download_url) as response, open(target_path, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
                
            return target_path
        except Exception as e:
            print(f"[Updater] Download failed: {e}")
            return None

    def run_update(self, file_path: str):
        """
        Launches the update file. 
        If it's an installer, it handles itself.
        If portable, we just show it in explorer? Or try to replace self?
        Replacing self while running is hard on Windows.
        So just show in folder for Portable.
        """
        if not file_path or not os.path.exists(file_path):
            return

        if file_path.endswith("Setup.exe"):
            # Launch Installer quiet? Or standard UI? Standard is better for user confidence.
            subprocess.Popen([file_path])
            sys.exit(0) # Close current app
        else:
            # Portable: Show in folder
            subprocess.Popen(f'explorer /select,"{file_path}"')
