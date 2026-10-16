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
    tag = 'v1.2'
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
        body_text = """# Crypt of the Necrolord v1.2 ⚔️💀

## 🚀 What's New in v1.2
- **Difficulty & Boss Tuning**:
  - Reverted aggressive Act 1 floor scaling and monster Strength buffs to ensure fair and satisfying progression.
  - Substantially nerfed boss damage, multi-hit flurries, and combat buffs across all major encounters (Necrolord Malakor, Void Behemoth, Ignis the Infernal, Archmage Valerius, The Corrupted Heart, Nemesis Avatar).
  - Restored Act Ascension Healing to **75% Max HP** and restored starting gold to **99 Gold**.
  - Reverted standard enemy damage spikes on Cultist, Skeletal Sentinel, Plague Fiend, and Void Reaver.
- **Character Survival Rebalance**:
  - Rebalanced core survivability across all 5 champions:
    - **Blood Knight**: 84 Max HP
    - **Shadow Assassin**: 75 Max HP
    - **Void Necromancer**: 76 Max HP (better offsets self-harm card sacrifices)
    - **Tempest Herald**: 76 Max HP
    - **Radiant Templar**: 88 Max HP
- **Radiant Templar Mechanics**:
  - **1-Turn Thorns**: Retaliation Thorns persists through the enemy turn to strike back against incoming attacks, then clears at the start of your next turn.
  - **Non-Stacking Thorns**: Re-applying Thorns refreshes to the maximum value rather than accumulating indefinitely.
- **Character-Exclusive Card Pools**:
  - Card rewards and shops now offer archetype cards unique to your chosen champion, alongside universal neutral spells.
- **Inspect Tooltips**:
  - Hovering over relics and potions across the top bar, merchant shop, and combat rewards displays stylized tooltips with full descriptions and effects.

## 📦 Downloads
- **Windows Setup Installer**: `CryptOfTheNecrolord_Setup_v1.2.0.exe` (Recommended - installs or cleanly updates existing game with desktop/start menu shortcuts)
- **Portable Zip**: `CryptOfTheNecrolord_v1.2.0_win64.zip` (Extract & play directly without installation)
"""
        create_payload = json.dumps({
            'tag_name': tag,
            'name': 'Crypt of the Necrolord v1.2',
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
        'CryptOfTheNecrolord_Setup_v1.2.0.exe',
        'CryptOfTheNecrolord_v1.2.0_win64.zip'
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
