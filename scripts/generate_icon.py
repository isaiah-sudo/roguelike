"""
Icon generator for Crypt of the Necrolord.
Generates multi-resolution .ico and high-resolution .png icons.
"""
from PIL import Image, ImageDraw, ImageFilter
import math
import os

def create_game_icon(size=512):
    # Render at high resolution then downsample for ultra-smooth anti-aliasing
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size // 2, size // 2
    radius = int(size * 0.45)

    # 1. Outer ethereal glow layer
    glow = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    for r in range(radius + 20, radius - 10, -3):
        alpha = int(45 * (1 - abs(r - radius) / 25.0))
        gdraw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(140, 40, 220, max(0, alpha)))
    glow = glow.filter(ImageFilter.GaussianBlur(12))
    img.paste(Image.alpha_composite(Image.new("RGBA", (size, size), (0,0,0,0)), glow), (0,0))

    # 2. Main Shield / Crest base (Gothic curved crest)
    crest_pts = [
        (cx - int(size * 0.38), cy - int(size * 0.36)),
        (cx, cy - int(size * 0.44)),
        (cx + int(size * 0.38), cy - int(size * 0.36)),
        (cx + int(size * 0.40), cy + int(size * 0.05)),
        (cx + int(size * 0.28), cy + int(size * 0.32)),
        (cx, cy + int(size * 0.46)),
        (cx - int(size * 0.28), cy + int(size * 0.32)),
        (cx - int(size * 0.40), cy + int(size * 0.05)),
    ]

    # Draw outer rim - dark gothic iron
    draw.polygon(crest_pts, fill=(24, 18, 32, 255))

    # Inner crest polygon
    inner_pts = []
    scale = 0.92
    for x, y in crest_pts:
        ix = cx + (x - cx) * scale
        iy = cy + (y - cy) * scale
        inner_pts.append((ix, iy))

    # Golden filigree rim
    draw.polygon(inner_pts, fill=(45, 30, 60, 255), outline=(212, 175, 55, 255), width=int(size * 0.015))

    # Dark inner cavity
    core_pts = []
    scale2 = 0.86
    for x, y in crest_pts:
        ix = cx + (x - cx) * scale2
        iy = cy + (y - cy) * scale2
        core_pts.append((ix, iy))
    draw.polygon(core_pts, fill=(15, 10, 22, 255), outline=(138, 43, 226, 180), width=int(size * 0.008))

    # 3. Ethereal Spire & Necrolord Crown / Skull
    # Spire peaks in background
    spire_color = (60, 35, 80, 220)
    draw.polygon([(cx, cy - int(size * 0.38)), (cx - 30, cy - int(size * 0.15)), (cx + 30, cy - int(size * 0.15))], fill=spire_color)
    draw.polygon([(cx - 70, cy - int(size * 0.32)), (cx - 95, cy - int(size * 0.12)), (cx - 45, cy - int(size * 0.12))], fill=spire_color)
    draw.polygon([(cx + 70, cy - int(size * 0.32)), (cx + 45, cy - int(size * 0.12)), (cx + 95, cy - int(size * 0.12))], fill=spire_color)

    # 4. Spiked Crown of the Necrolord
    crown_y = cy - int(size * 0.18)
    crown_pts = [
        (cx - int(size * 0.22), crown_y + 15),
        (cx - int(size * 0.25), crown_y - int(size * 0.12)),  # left peak
        (cx - int(size * 0.12), crown_y - 10),
        (cx, crown_y - int(size * 0.18)),                     # center tall peak
        (cx + int(size * 0.12), crown_y - 10),
        (cx + int(size * 0.25), crown_y - int(size * 0.12)),  # right peak
        (cx + int(size * 0.22), crown_y + 15),
    ]
    draw.polygon(crown_pts, fill=(35, 25, 45, 255), outline=(255, 215, 0, 240), width=int(size * 0.012))

    # Crown central blood ruby
    gem_y = crown_y - int(size * 0.05)
    draw.polygon([(cx, gem_y - 18), (cx + 12, gem_y), (cx, gem_y + 18), (cx - 12, gem_y)], fill=(230, 30, 60, 255), outline=(255, 180, 190, 255), width=2)

    # 5. Stylized Necromancer Skull Face
    skull_y = cy + int(size * 0.06)
    # Cranium
    draw.ellipse([cx - int(size * 0.20), skull_y - int(size * 0.22), cx + int(size * 0.20), skull_y + int(size * 0.08)], fill=(210, 205, 225, 255))
    # Cheek taper
    jaw_pts = [
        (cx - int(size * 0.16), skull_y - 5),
        (cx - int(size * 0.10), skull_y + int(size * 0.22)),
        (cx + int(size * 0.10), skull_y + int(size * 0.22)),
        (cx + int(size * 0.16), skull_y - 5),
    ]
    draw.polygon(jaw_pts, fill=(195, 190, 215, 255))

    # Temples / shadows
    draw.polygon([(cx - int(size * 0.20), skull_y), (cx - int(size * 0.13), skull_y), (cx - int(size * 0.16), skull_y - 25)], fill=(40, 30, 50, 255))
    draw.polygon([(cx + int(size * 0.20), skull_y), (cx + int(size * 0.13), skull_y), (cx + int(size * 0.16), skull_y - 25)], fill=(40, 30, 50, 255))

    # Glowing Eye Sockets (Dark angular hollows)
    eye_offset_x = int(size * 0.085)
    eye_y = skull_y - int(size * 0.04)
    # Left eye cavity
    draw.polygon([(cx - eye_offset_x - 22, eye_y - 12), (cx - eye_offset_x + 18, eye_y - 6), (cx - eye_offset_x, eye_y + 24)], fill=(12, 8, 16, 255))
    # Right eye cavity
    draw.polygon([(cx + eye_offset_x + 22, eye_y - 12), (cx + eye_offset_x - 18, eye_y - 6), (cx + eye_offset_x, eye_y + 24)], fill=(12, 8, 16, 255))

    # Nasal cavity
    draw.polygon([(cx, skull_y + 12), (cx + 8, skull_y + 35), (cx - 8, skull_y + 35)], fill=(18, 12, 22, 255))

    # Teeth / jaw slits
    teeth_y = skull_y + int(size * 0.12)
    draw.line([(cx - int(size * 0.09), teeth_y), (cx + int(size * 0.09), teeth_y)], fill=(30, 20, 38, 255), width=int(size * 0.008))
    for tx in range(-int(size * 0.07), int(size * 0.08), int(size * 0.028)):
        draw.line([(cx + tx, teeth_y - 10), (cx + tx, teeth_y + 10)], fill=(30, 20, 38, 255), width=3)

    # 6. Flaming Ethereal Soul Flames in Eyes (Crimson / Violet fire)
    # Left eye flame
    draw.ellipse([cx - eye_offset_x - 10, eye_y - 5, cx - eye_offset_x + 8, eye_y + 15], fill=(240, 30, 80, 255))
    draw.ellipse([cx - eye_offset_x - 5, eye_y, cx - eye_offset_x + 4, eye_y + 10], fill=(255, 230, 160, 255))

    # Right eye flame
    draw.ellipse([cx + eye_offset_x - 8, eye_y - 5, cx + eye_offset_x + 10, eye_y + 15], fill=(240, 30, 80, 255))
    draw.ellipse([cx + eye_offset_x - 4, eye_y, cx + eye_offset_x + 5, eye_y + 10], fill=(255, 230, 160, 255))

    # 7. Crossed Runeblades behind shield bottom
    draw.line([(cx - int(size * 0.28), cy + int(size * 0.26)), (cx + int(size * 0.28), cy + int(size * 0.46))], fill=(180, 150, 60, 255), width=int(size * 0.016))
    draw.line([(cx + int(size * 0.28), cy + int(size * 0.26)), (cx - int(size * 0.28), cy + int(size * 0.46))], fill=(180, 150, 60, 255), width=int(size * 0.016))

    return img

def generate_icons():
    print("Generating high-res base icon (512x512)...")
    base_img = create_game_icon(512)

    os.makedirs("assets", exist_ok=True)

    # 256x256 PNG for pygame window and high-DPI displays
    icon_256 = base_img.resize((256, 256), Image.Resampling.LANCZOS)
    icon_png_path = os.path.join("assets", "icon.png")
    icon_256.save(icon_png_path, "PNG")
    print(f"Saved: {icon_png_path}")

    # Generate multi-resolution ICO for Windows
    sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (24, 24), (16, 16)]
    icon_ico_path = os.path.join("assets", "icon.ico")
    icon_256.save(icon_ico_path, format="ICO", sizes=sizes)
    print(f"Saved: {icon_ico_path} with sizes {sizes}")

    # Copy / save as app.ico as well
    app_ico_path = os.path.join("assets", "app.ico")
    icon_256.save(app_ico_path, format="ICO", sizes=sizes)
    print(f"Saved: {app_ico_path}")

if __name__ == "__main__":
    generate_icons()
