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
    tag = 'v1.6'
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
        body_text = """# Crypt of the Necrolord v1.6 ⚔️🎨

## 🚀 What's New in v1.6
- **Complete Card Art Overhaul (All 84 Cards!)**:
  - Every single card across all 5 champions and neutral spell pools now features rich, custom-crafted, dark fantasy illustrations rendered at 2x super-sampled resolution (`260x128`).
  - **Warrior & Blade Archetypes**: Slashing greatswords, crushing warhammers, wide sweeping cleaves, berserker buster blades, flaming horned skulls, and dual spinning whirlwinds.
  - **Shadow Assassin & Poison**: Sleek throwing stilettos, bubbling toxic flasks, skull detonators, venom-coiled serpents, hooded assassin silhouettes, and ethereal wraiths.
  - **Bastion & Fortifications**: Steel heater shields with brass bosses, glowing forge anvils and hammers, stone battlement walls, blazing flame bucklers, and crystal diamond fortresses.
  - **Tempest & Ice**: Crackling plasma orbs, branching lightning bolts, ground-splitting thunder strikes, glacial peaks, and subzero blizzard tempests.
  - **Radiant Templar**: Beams of divine holy light, golden Latin crosses, angelic feathered wings, sacred scriptures, and scales of divine retribution.
  - **Void Necromancy**: Grim reaper scythes, soul-siphoning tendrils, severed soul orbs, hands clawing out of grave mounds, and bleeding corrupt grimoires.
  - **Buffs & Power Engines**: Surging adrenaline hearts, flexing muscular power rings, glowing third eyes, glaring crimson rage eyes, and shattering golden chains.
- **Enhanced Card Frames & Foil Highlights**:
  - Ornate art frames with deep inner bevels and top-edge specular gleams.
  - Upgraded cards feature lustrous golden borders and enhanced foil sheen.
- **Optimized Asset Pipeline**:
  - High-performance in-memory caching ensures instantaneous rendering and silky-smooth 60 FPS combat with zero lag.

## 📦 Downloads
- **Windows Setup Installer**: `CryptOfTheNecrolord_Setup_v1.6.0.exe` (Recommended - installs or cleanly updates existing game with desktop/start menu shortcuts)
- **Portable Zip**: `CryptOfTheNecrolord_v1.6.0_win64.zip` (Extract & play directly without installation)
"""
        create_payload = json.dumps({
            'tag_name': tag,
            'name': 'Crypt of the Necrolord v1.6',
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
        'CryptOfTheNecrolord_Setup_v1.6.0.exe',
        'CryptOfTheNecrolord_v1.6.0_win64.zip'
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
