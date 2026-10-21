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
    tag = 'v1.6.2'
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
        body_text = """# Crypt of the Necrolord v1.6.2 ⚔️🛡️

## 🚀 What's New in v1.6.2
- **Envenom Overhaul**:
  - Fully implemented the missing Envenom status pipeline: Attacks dealing unblocked damage now consistently apply Poison stacks equal to Envenom stacks, with animated toxic particle effects and popups.
- **Maximum Hand Limit (10 Cards)**:
  - Capped active hand size to 10 cards across all draw mechanics, card generation spells (Blade Dance, Cloak & Dagger, Storm of Steel), and relic triggers.
  - Re-centered hand rendering layout in combat to prevent 10-card hands from overlapping the End Turn button.
- **Power Cards Exhaust on Cast**:
  - All Power cards (rendered with purple banners) now exhaust upon resolution so persistent combat powers are consumed and never cycled back into the draw pile.
- **Anger Infinite Loop Prevention**:
  - Duplicated copies of Anger now possess Exhaust and do not chain-duplicate.
  - Added a maximum cap of 3 Anger casts per turn with interactive visual feedback if exceeded.
- **Rebalanced Block + Card Draw**:
  - `Warcry`: Rebalanced from 0 energy to 1 energy; increased block from 4 (upgraded 6) to 6 Block, Draw 1 (upgraded 9 Block, Draw 2).
  - `Shadowstep`: Rebalanced from 0 energy to 1 energy; increased block from 4 (upgraded 7) to 6 Block, Draw 1 (upgraded 9 Block, Draw 2).
  - `Divine Favor`: Rebalanced from 0 energy to 1 energy; increased block from 4 (upgraded 7) to Draw 2, Gain 5 Block (upgraded Draw 2, Gain 8 Block), with full Dexterity scaling.

## 📦 Downloads
- **Windows Setup Installer**: `CryptOfTheNecrolord_Setup_v1.6.2.exe` (Recommended - clean install / upgrade with desktop shortcuts)
- **Portable Zip**: `CryptOfTheNecrolord_v1.6.2_win64.zip` (Extract & play directly without installation)
"""
        create_payload = json.dumps({
            'tag_name': tag,
            'name': 'Crypt of the Necrolord v1.6.2',
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
        'CryptOfTheNecrolord_Setup_v1.6.2.exe',
        'CryptOfTheNecrolord_v1.6.2_win64.zip'
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
