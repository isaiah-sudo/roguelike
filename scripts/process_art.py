"""
Robust sprite and portrait generator for Crypt of the Necrolord.
Extracts characters and monsters, removes solid backgrounds, and saves them to game assets.
"""
import os
from collections import deque
from PIL import Image, ImageFilter
import numpy as np

HEROES = [
    {
        "id": "blood_knight",
        "path": r"C:\Users\timme\.gemini\antigravity\brain\f9fc1ffb-5473-4784-b336-d8a2191403f9\blood_knight_sprite_1792424106096.jpg",
        "name": "Blood Knight"
    },
    {
        "id": "shadow_assassin",
        "path": r"C:\Users\timme\.gemini\antigravity\brain\f9fc1ffb-5473-4784-b336-d8a2191403f9\shadow_assassin_dark_bg_1792424195364.jpg",
        "name": "Shadow Assassin"
    },
    {
        "id": "void_necromancer",
        "path": r"C:\Users\timme\.gemini\antigravity\brain\f9fc1ffb-5473-4784-b336-d8a2191403f9\void_necromancer_1792424157443.jpg",
        "name": "Void Necromancer"
    },
    {
        "id": "tempest_herald",
        "path": r"C:\Users\timme\.gemini\antigravity\brain\f9fc1ffb-5473-4784-b336-d8a2191403f9\tempest_herald_1792424158409.jpg",
        "name": "Tempest Herald"
    },
    {
        "id": "radiant_templar",
        "path": r"C:\Users\timme\.gemini\antigravity\brain\f9fc1ffb-5473-4784-b336-d8a2191403f9\radiant_templar_1792424156997.jpg",
        "name": "Radiant Templar"
    }
]

ENEMIES = [
    {
        "id": "cultist",
        "path": r"C:\Users\timme\.gemini\antigravity\brain\f9fc1ffb-5473-4784-b336-d8a2191403f9\crypt_cultist_1792424265908.jpg",
        "name": "Crypt Cultist"
    },
    {
        "id": "skeleton_sentinel",
        "path": r"C:\Users\timme\.gemini\antigravity\brain\f9fc1ffb-5473-4784-b336-d8a2191403f9\skeleton_sentinel_1792424263827.jpg",
        "name": "Skeleton Sentinel"
    },
    {
        "id": "dread_spider",
        "path": r"C:\Users\timme\.gemini\antigravity\brain\f9fc1ffb-5473-4784-b336-d8a2191403f9\dread_spider_sprite_1792424294374.jpg",
        "name": "Dread Spider"
    },
    {
        "id": "void_reaver",
        "path": r"C:\Users\timme\.gemini\antigravity\brain\f9fc1ffb-5473-4784-b336-d8a2191403f9\void_reaver_sprite_1792424267256.jpg",
        "name": "Void Reaver"
    },
    {
        "id": "necrolord_malakor",
        "path": r"C:\Users\timme\.gemini\antigravity\brain\f9fc1ffb-5473-4784-b336-d8a2191403f9\necrolord_malakor_1792424271701.jpg",
        "name": "Necrolord Malakor"
    }
]

def remove_background(img: Image.Image) -> Image.Image:
    img = img.convert('RGBA')
    arr = np.array(img, dtype=np.float32)
    h, w, _ = arr.shape

    # Sample corners to determine background color
    corners = np.array([
        arr[0, 0, :3], arr[0, w - 1, :3],
        arr[h - 1, 0, :3], arr[h - 1, w - 1, :3]
    ])
    bg_color = np.mean(corners, axis=0)
    is_dark = np.mean(bg_color) < 128

    rgb = arr[:, :, :3]
    if is_dark:
        # Distance from black/dark bg
        dist = np.linalg.norm(rgb - bg_color, axis=2)
        # Also max channel threshold
        max_c = np.max(rgb, axis=2)
        bg_candidate = (dist < 45) | (max_c < 28)
    else:
        # Distance from white/light bg
        dist = np.linalg.norm(rgb - bg_color, axis=2)
        min_c = np.min(rgb, axis=2)
        bg_candidate = (dist < 50) | (min_c > 230)

    # Flood fill only pixels connected to borders
    visited = np.zeros((h, w), dtype=bool)
    q = deque()

    for x in range(w):
        if bg_candidate[0, x]:
            visited[0, x] = True
            q.append((0, x))
        if bg_candidate[h - 1, x]:
            visited[h - 1, x] = True
            q.append((h - 1, x))
    for y in range(h):
        if bg_candidate[y, 0]:
            visited[y, 0] = True
            q.append((y, 0))
        if bg_candidate[y, w - 1]:
            visited[y, w - 1] = True
            q.append((y, w - 1))

    while q:
        y, x = q.popleft()
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx]:
                if bg_candidate[ny, nx]:
                    visited[ny, nx] = True
                    q.append((ny, nx))

    # Mask: 0 for background, 255 for sprite
    alpha_mask = np.where(visited, 0, 255).astype(np.uint8)

    # Smooth the mask slightly for clean edges
    mask_img = Image.fromarray(alpha_mask, mode='L')
    # Use slight blur on mask for soft anti-aliased edge
    mask_img = mask_img.filter(ImageFilter.GaussianBlur(radius=0.7))

    final_arr = np.array(img)
    final_arr[:, :, 3] = np.array(mask_img)

    result = Image.fromarray(final_arr, mode='RGBA')
    # Tight crop
    bbox = result.getbbox()
    if bbox:
        pad = 8
        crop_box = (
            max(0, bbox[0] - pad),
            max(0, bbox[1] - pad),
            min(w, bbox[2] + pad),
            min(h, bbox[3] + pad)
        )
        result = result.crop(crop_box)
    return result

def create_card_portrait(src_img: Image.Image, output_path: str, target_size=(200, 130)):
    """Creates a stylized landscape/framed portrait for character select cards."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img = src_img.convert('RGB')
    w, h = img.size

    # Crop upper-body (head and shoulders focus)
    crop_w = int(w * 0.7)
    crop_h = int(crop_w * (target_size[1] / target_size[0]))
    left = (w - crop_w) // 2
    top = int(h * 0.05)
    right = left + crop_w
    bottom = top + crop_h

    crop_img = img.crop((left, top, right, bottom))
    resized = crop_img.resize(target_size, Image.Resampling.LANCZOS)
    resized.save(output_path, "PNG")
    print(f"Created portrait: {output_path}")

def run_pipeline():
    base_dir = r"c:\Users\timme\Documents\GitHub\rougelike\assets"
    char_sprite_dir = os.path.join(base_dir, "sprites", "characters")
    enemy_sprite_dir = os.path.join(base_dir, "sprites", "enemies")
    portrait_dir = os.path.join(base_dir, "portraits")

    os.makedirs(char_sprite_dir, exist_ok=True)
    os.makedirs(enemy_sprite_dir, exist_ok=True)
    os.makedirs(portrait_dir, exist_ok=True)

    print("--- Processing Heroes ---")
    for hero in HEROES:
        src = Image.open(hero["path"])
        # 1. Full transparent sprite
        sprite = remove_background(src)
        sprite_path = os.path.join(char_sprite_dir, f"{hero['id']}.png")
        sprite.save(sprite_path, "PNG")
        print(f"Saved hero sprite: {sprite_path} {sprite.size}")

        # 2. Card portrait
        portrait_path = os.path.join(portrait_dir, f"{hero['id']}.png")
        create_card_portrait(src, portrait_path)

    print("--- Processing Enemies ---")
    for enemy in ENEMIES:
        src = Image.open(enemy["path"])
        sprite = remove_background(src)
        sprite_path = os.path.join(enemy_sprite_dir, f"{enemy['id']}.png")
        sprite.save(sprite_path, "PNG")
        print(f"Saved enemy sprite: {sprite_path} {sprite.size}")

if __name__ == "__main__":
    run_pipeline()
