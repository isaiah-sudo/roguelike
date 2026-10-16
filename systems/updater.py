"""
Automated Update System for Crypt of the Necrolord.
Handles background checking for GitHub releases, asset downloading, progress tracking,
and seamless installer execution.
"""
import os
import sys
import json
import enum
import logging
import tempfile
import threading
import urllib.request
import urllib.error
import subprocess
import webbrowser
from typing import Optional, Dict, Any, Tuple, Callable

from settings import GAME_VERSION, GITHUB_REPO

logger = logging.getLogger("updater")


class UpdateState(enum.Enum):
    IDLE = "idle"
    CHECKING = "checking"
    UP_TO_DATE = "up_to_date"
    UPDATE_AVAILABLE = "update_available"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    APPLYING = "applying"
    ERROR = "error"


def parse_version(ver_str: str) -> Tuple[int, ...]:
    """
    Parses a version string into a comparable tuple of integers.
    Examples:
        'v1.2' -> (1, 2, 0)
        'v1.2.0' -> (1, 2, 0)
        '1.3.5' -> (1, 3, 5)
        'v2.0-beta' -> (2, 0, 0)
    """
    if not ver_str:
        return (0, 0, 0)
    
    cleaned = ver_str.strip().lstrip('vV')
    # Split on first hyphen or plus for pre-releases
    main_part = cleaned.split('-')[0].split('+')[0]
    
    parts = []
    for chunk in main_part.split('.'):
        digits = ''.join(c for c in chunk if c.isdigit())
        if digits:
            parts.append(int(digits))
        else:
            break
            
    while len(parts) < 3:
        parts.append(0)
        
    return tuple(parts)


def is_newer_version(remote_ver_str: str, current_ver_str: str) -> bool:
    """Returns True if remote version is strictly greater than current version."""
    return parse_version(remote_ver_str) > parse_version(current_ver_str)


def select_best_asset(assets: list) -> Optional[Dict[str, Any]]:
    """
    Selects the most suitable update asset from release assets.
    Priority on Windows:
    1. .exe containing 'setup' or 'installer'
    2. Any .exe file
    3. Any .zip file
    4. First asset available
    """
    if not assets:
        return None
        
    # 1. Setup .exe
    for a in assets:
        name = a.get("name", "").lower()
        if name.endswith(".exe") and ("setup" in name or "installer" in name):
            return a
            
    # 2. Any .exe
    for a in assets:
        name = a.get("name", "").lower()
        if name.endswith(".exe"):
            return a
            
    # 3. Any .zip
    for a in assets:
        name = a.get("name", "").lower()
        if name.endswith(".zip"):
            return a
            
    # 4. Fallback to first
    return assets[0]


class UpdateInfo:
    """Information regarding an available update."""
    def __init__(self, tag_name: str, title: str, body: str, html_url: str,
                 asset_name: str, asset_url: str, asset_size: int):
        self.tag_name = tag_name
        self.version_str = tag_name.lstrip('vV')
        self.title = title
        self.body = body
        self.html_url = html_url
        self.asset_name = asset_name
        self.asset_url = asset_url
        self.asset_size = asset_size

    def __repr__(self):
        return f"<UpdateInfo {self.tag_name} ({self.asset_name})>"


class UpdateManager:
    """
    Manages checking, downloading, and applying game updates.
    Runs network operations asynchronously to never block game rendering.
    """
    def __init__(self, current_version: str = GAME_VERSION, repo: str = GITHUB_REPO):
        self.current_version = current_version
        self.repo = repo
        self.state = UpdateState.IDLE
        self.lock = threading.Lock()
        
        self.update_info: Optional[UpdateInfo] = None
        self.downloaded_path: Optional[str] = None
        self.error_message: Optional[str] = None
        
        self.bytes_downloaded = 0
        self.total_bytes = 0
        self.progress = 0.0  # 0.0 to 1.0
        
        self._check_thread: Optional[threading.Thread] = None
        self._download_thread: Optional[threading.Thread] = None
        self._cancel_flag = False

    def check_for_updates(self, async_check: bool = True):
        """Initiates update check."""
        with self.lock:
            if self.state in (UpdateState.CHECKING, UpdateState.DOWNLOADING):
                return
            self.state = UpdateState.CHECKING
            self.error_message = None

        if async_check:
            self._check_thread = threading.Thread(target=self._run_check, daemon=True)
            self._check_thread.start()
        else:
            self._run_check()

    def _run_check(self):
        """Worker thread to query GitHub Releases API."""
        api_url = f"https://api.github.com/repos/{self.repo}/releases/latest"
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CryptOfTheNecrolord-Updater"
        }
        req = urllib.request.Request(api_url, headers=headers)
        
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            # 404 might mean no release exists yet
            with self.lock:
                if e.code == 404:
                    self.state = UpdateState.UP_TO_DATE
                else:
                    self.state = UpdateState.ERROR
                    self.error_message = f"HTTP Error {e.code}"
            return
        except Exception as e:
            with self.lock:
                self.state = UpdateState.ERROR
                self.error_message = f"Check failed: {str(e)[:40]}"
            return

        tag_name = data.get("tag_name", "")
        remote_ver = tag_name.lstrip('vV')

        if is_newer_version(remote_ver, self.current_version):
            assets = data.get("assets", [])
            chosen_asset = select_best_asset(assets)
            
            asset_name = chosen_asset.get("name", "") if chosen_asset else ""
            asset_url = chosen_asset.get("browser_download_url", "") if chosen_asset else ""
            asset_size = chosen_asset.get("size", 0) if chosen_asset else 0

            info = UpdateInfo(
                tag_name=tag_name,
                title=data.get("name") or f"Crypt of the Necrolord {tag_name}",
                body=data.get("body", ""),
                html_url=data.get("html_url", f"https://github.com/{self.repo}/releases"),
                asset_name=asset_name,
                asset_url=asset_url,
                asset_size=asset_size
            )
            with self.lock:
                self.update_info = info
                self.state = UpdateState.UPDATE_AVAILABLE
        else:
            with self.lock:
                self.state = UpdateState.UP_TO_DATE

    def start_download(self, async_download: bool = True):
        """Begins downloading the update asset."""
        with self.lock:
            if not self.update_info or not self.update_info.asset_url:
                self.state = UpdateState.ERROR
                self.error_message = "No download URL available"
                return
            if self.state == UpdateState.DOWNLOADING:
                return
            self.state = UpdateState.DOWNLOADING
            self.bytes_downloaded = 0
            self.total_bytes = self.update_info.asset_size
            self.progress = 0.0
            self.error_message = None
            self._cancel_flag = False

        if async_download:
            self._download_thread = threading.Thread(target=self._run_download, daemon=True)
            self._download_thread.start()
        else:
            self._run_download()

    def _run_download(self):
        """Worker thread to stream download the asset into temp directory."""
        info = self.update_info
        if not info or not info.asset_url:
            return

        # Prepare destination directory
        temp_dir = os.path.join(tempfile.gettempdir(), "CryptOfTheNecrolord_Updates")
        os.makedirs(temp_dir, exist_ok=True)
        dest_path = os.path.join(temp_dir, info.asset_name)

        headers = {
            "User-Agent": "CryptOfTheNecrolord-Updater",
            "Accept": "application/octet-stream"
        }
        req = urllib.request.Request(info.asset_url, headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                content_len = resp.headers.get("Content-Length")
                if content_len:
                    with self.lock:
                        self.total_bytes = int(content_len)

                downloaded = 0
                chunk_size = 64 * 1024  # 64 KB chunks
                
                with open(dest_path, "wb") as f:
                    while True:
                        if self._cancel_flag:
                            return
                        chunk = resp.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        with self.lock:
                            self.bytes_downloaded = downloaded
                            if self.total_bytes > 0:
                                self.progress = min(1.0, downloaded / self.total_bytes)

            with self.lock:
                self.downloaded_path = dest_path
                self.progress = 1.0
                self.state = UpdateState.DOWNLOADED
                
        except Exception as e:
            with self.lock:
                self.state = UpdateState.ERROR
                self.error_message = f"Download error: {str(e)[:40]}"

    def apply_update(self) -> bool:
        """
        Executes the downloaded installer or opens the update package.
        Returns True if the game should terminate to let update proceed.
        """
        with self.lock:
            file_path = self.downloaded_path
            info = self.update_info

        if not file_path or not os.path.exists(file_path):
            if info and info.html_url:
                webbrowser.open(info.html_url)
            return False

        with self.lock:
            self.state = UpdateState.APPLYING

        # On Windows, launch installer executable
        if file_path.lower().endswith(".exe"):
            try:
                # Launching with subprocess detached so installer continues after game exits
                flags = 0
                if sys.platform == "win32":
                    flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
                subprocess.Popen([file_path], creationflags=flags, close_fds=True)
                return True
            except Exception as e:
                # Fallback to os.startfile
                try:
                    os.startfile(file_path)
                    return True
                except Exception as ex:
                    with self.lock:
                        self.state = UpdateState.ERROR
                        self.error_message = f"Could not launch installer: {ex}"
                    return False
        else:
            # If a zip or other asset, reveal in explorer / directory
            try:
                if sys.platform == "win32":
                    os.startfile(os.path.dirname(file_path))
                else:
                    subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", os.path.dirname(file_path)])
                return True
            except Exception:
                if info and info.html_url:
                    webbrowser.open(info.html_url)
                return False

    def cancel(self):
        """Cancels any running download."""
        self._cancel_flag = True
