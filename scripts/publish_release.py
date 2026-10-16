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

    repo = 'isaiah-sudo/rougelike'
    tag = 'v1.1'
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
        body_text = """# Crypt of the Necrolord v1.1 ⚔️💀

## 🚀 What's New in v1.1
- **Full Deck, Smithing & Purge Scrolling**:
  - Smooth vertical scrolling across the entire deck view, campfire smithing/upgrade screen, and merchant purge ritual screen.
  - Supports mouse wheel, draggable custom scrollbar, and keyboard navigation with full viewport clipping.
  - Added convenient **CANCEL** buttons to both the card upgrade and card purge screens.
- **Clean In-Place Update & Save Preservation**:
  - The new Windows setup installer cleanly detects your existing installation and updates files in-place without overwriting or deleting your saved runs.
  - Automatically handles running instances of the game before updating to prevent file locking.
- **Combat Balance Overhaul**:
  - Progressive depth and act monster scaling: deeper floors and higher acts dynamically scale monster vitality, strength, and elite/boss modifiers.
  - Balanced act ascension healing from 75% down to 40% Max HP.
  - Tuned starting economy and balanced relics (e.g., Sun Crest Retribution).
  - Increased threat levels on early enemies (Cultist, Sentinel, Plague Fiend).
- **Major Visual & Animation Polish**:
  - **Trailing Ghost HP Bars**: Fighting game / AAA roguelike delayed amber damage bars on entities that smoothly slide down after attacks.
  - **Animated Campfire**: Undulating multi-layered flame tongues, hot rising embers drifting upward, pulsing warm radial light, and glowing coals.
  - **Card Visuals Overhaul**: Golden corner ribbons and metallic frames on upgraded cards, glowing hover halo auras, 3D beveled energy orbs, and gemstone rarity indicators.
  - **Targeting Reticle**: Animated pulsing crosshairs with rotating brackets over targeted enemies.
  - **Atmospheric Particles & Shockwaves**: Expanding attack shockwave rings, floating dungeon air motes, and lantern-lit merchant shop.

## 📦 Downloads
- **Windows Setup Installer**: `CryptOfTheNecrolord_Setup_v1.1.0.exe` (Recommended - installs or cleanly updates existing game with desktop/start menu shortcuts)
- **Portable Zip**: `CryptOfTheNecrolord_v1.1.0_win64.zip` (Extract & play directly without installation)
"""
        create_payload = json.dumps({
            'tag_name': tag,
            'name': 'Crypt of the Necrolord v1.1',
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
        'CryptOfTheNecrolord_Setup_v1.1.0.exe',
        'CryptOfTheNecrolord_v1.1.0_win64.zip'
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
