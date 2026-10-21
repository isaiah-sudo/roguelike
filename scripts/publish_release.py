"""
Automated GitHub Release Publisher & Asset Uploader for Crypt of the Necrolord.
"""
import os
import sys
import json
import urllib.request
import urllib.error
import subprocess

def get_github_token() -> str:
    proc = subprocess.Popen(['git', 'credential', 'fill'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    out, _ = proc.communicate('protocol=https\nhost=github.com\n')
    creds = dict(line.split('=', 1) for line in out.strip().splitlines() if '=' in line)
    return creds.get('password')

def main():
    token = get_github_token()
    if not token:
        print("[ERROR] Could not retrieve GitHub token from git credentials.")
        sys.exit(1)

    repo = 'isaiah-sudo/roguelike'
    tag = 'v1.6.3'
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'CryptOfTheNecrolord-Publisher'
    }

    print(f"Checking for release with tag {tag} in {repo}...")
    req = urllib.request.Request(f'https://api.github.com/repos/{repo}/releases/tags/{tag}', headers=headers)
    release = None
    try:
        with urllib.request.urlopen(req) as resp:
            release = json.loads(resp.read().decode())
            print(f"Found existing release ID: {release['id']}")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("Release not found, creating new release...")
        else:
            raise

    if not release:
        body_text = """# Crypt of the Necrolord v1.6.3 ⚔️🛡️

## 🚀 What's New in v1.6.3
- **Multi-Act Map Scrolling & Preview**:
  - **Vertical Spire Navigation**: Freely scroll up through the spire map to preview future acts (**Act II: The Sunken Citadel**, **Act III: The Abyssal Spire**, and **Spire Pinnacle: Malakor's Sanctum**), and scroll down to inspect past achievements.
  - **Flexible Controls**: Smooth camera panning via mouse wheel, click-and-drag map background panning, or arrow keys (`Up` / `Down` / `PgUp` / `PgDn` / `Home` / `End`).
  - **Quick Jump Navigation Pills**: Top banner buttons (`[ACT I]`, `[ACT II]`, `[ACT III]`, and `[CURRENT]`) snap directly to any act or focus instantly back on your current player floor.
  - **Stone Gateway Dividers & Visual Hierarchy**: Thematic gateway banners separate each act with atmospheric viewport lighting.
  - **Preview & Path Integrity**: Locked nodes in future acts are styled with preview tooltips and protected from accidental clicks; completed acts preserve historical golden path lines.
- **Audio & SFX Hardening**:
  - Resolved an SFX playback error that could cause stability issues in combat and view transitions.
- **Multi-Act Save State Persistence**:
  - Run seeds and multi-act floor topologies serialize cleanly to save slots, preserving full dungeon state between sessions.

## 📦 Downloads
- **Windows Setup Installer**: `CryptOfTheNecrolord_Setup_v1.6.3.exe` (Recommended - clean install / upgrade with desktop shortcuts)
- **Portable Zip**: `CryptOfTheNecrolord_v1.6.3_win64.zip` (Extract & play directly without installation)
"""
        create_payload = json.dumps({
            'tag_name': tag,
            'name': 'Crypt of the Necrolord v1.6.3',
            'body': body_text,
            'draft': False,
            'prerelease': False
        }).encode('utf-8')
        create_req = urllib.request.Request(
            f'https://api.github.com/repos/{repo}/releases',
            data=create_payload,
            headers={**headers, 'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(create_req) as resp:
            release = json.loads(resp.read().decode())
            print(f"Successfully created release ID: {release['id']}")

    release_id = release['id']

    # Retrieve current assets on this release
    existing_assets = {a['name']: a['id'] for a in release.get('assets', [])}
    output_dir = 'installer_output'
    files_to_upload = [
        'CryptOfTheNecrolord_Setup_v1.6.3.exe',
        'CryptOfTheNecrolord_v1.6.3_win64.zip'
    ]

    for filename in files_to_upload:
        filepath = os.path.join(output_dir, filename)
        if not os.path.exists(filepath):
            print(f"[WARNING] File {filepath} not found, skipping.")
            continue

        if filename in existing_assets:
            asset_id = existing_assets[filename]
            print(f"Deleting older asset {filename} ({asset_id})...")
            del_req = urllib.request.Request(
                f'https://api.github.com/repos/{repo}/releases/assets/{asset_id}',
                headers=headers,
                method='DELETE'
            )
            with urllib.request.urlopen(del_req) as resp:
                pass

        file_size = os.path.getsize(filepath)
        print(f"Uploading {filename} ({file_size:,} bytes)...")
        upload_url = f'https://uploads.github.com/repos/{repo}/releases/{release_id}/assets?name={filename}'

        with open(filepath, 'rb') as f:
            file_bytes = f.read()

        up_headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/octet-stream',
            'User-Agent': 'CryptOfTheNecrolord-Publisher',
            'Accept': 'application/vnd.github.v3+json'
        }
        up_req = urllib.request.Request(upload_url, data=file_bytes, headers=up_headers)
        with urllib.request.urlopen(up_req) as resp:
            asset_info = json.loads(resp.read().decode())
            print(f"SUCCESS: Uploaded {filename}!")
            print(f"Direct download link: {asset_info.get('browser_download_url')}")

    print("\nAll release assets uploaded successfully to GitHub!")

if __name__ == '__main__':
    main()
