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
    tag = 'v1.6.5'
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
        body_text = """# Crypt of the Necrolord v1.6.5 ⚔️🛡️

## 🚀 What's New in v1.6.5
- **Classic Map View Restored**:
  - Reverted the multi-act scrolling view to restore the classic, clean, and intuitive single-act dungeon map overview.
- **Audio & SFX Crash Hardening**:
  - Fixed an SFX playback crash in combat and map view transitions with hardened audio exception safeguards.
- **Card Balance & Mechanics Polish**:
  - Envenom status pipeline fully active (attacks applying poison on unblocked damage).
  - Maximum hand limit capped at 10 cards across all draws and card generation effects.
  - Power cards exhaust on cast to prevent redundant cycling.
  - Anger infinite loop prevented with duplicate exhaust tags and 3-cast turn cap.
  - Rebalanced block + card draw skills (Warcry, Shadowstep, Divine Favor).

## 📦 Downloads
- **Windows Setup Installer**: `CryptOfTheNecrolord_Setup_v1.6.5.exe` (Recommended - clean install / upgrade with desktop shortcuts)
- **Portable Zip**: `CryptOfTheNecrolord_v1.6.5_win64.zip` (Extract & play directly without installation)
"""
        create_payload = json.dumps({
            'tag_name': tag,
            'name': 'Crypt of the Necrolord v1.6.5',
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
        'CryptOfTheNecrolord_Setup_v1.6.5.exe',
        'CryptOfTheNecrolord_v1.6.5_win64.zip'
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
