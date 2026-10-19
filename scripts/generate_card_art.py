"""
Comprehensive Card Art Generator for Crypt of the Necrolord.
Generates rich, dark fantasy 260x128 art illustrations for all 84 cards in the game.
"""
import os
import math
import random
from PIL import Image, ImageDraw, ImageFilter
import numpy as np

W = 260
H = 128
CENTER = (W // 2, H // 2)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "cards")

# ==============================================================================
# Background & Compositing Primitives
# ==============================================================================

def make_bg(top_col, bot_col, glow_col=None, glow_pos=CENTER, glow_r=85):
    """Generates a smooth linear gradient background with optional radial glow and subtle vignette."""
    y = np.linspace(0, 1, H)[:, None]
    top = np.array(top_col, dtype=np.float32)
    bot = np.array(bot_col, dtype=np.float32)
    base = np.tile((top * (1.0 - y) + bot * y)[:, None, :], (1, W, 1))

    if glow_col:
        yy, xx = np.mgrid[:H, :W]
        dist = np.sqrt((xx - glow_pos[0])**2 + (yy - glow_pos[1])**2)
        glow_factor = np.clip(1.0 - (dist / glow_r), 0.0, 1.0)**2.0
        g_col = np.array(glow_col[:3], dtype=np.float32)
        alpha = glow_col[3] / 255.0 if len(glow_col) > 3 else 0.75
        base = base * (1.0 - glow_factor[:, :, None] * alpha) + g_col * (glow_factor[:, :, None] * alpha)

    # Dark Vignette
    yy, xx = np.mgrid[:H, :W]
    dx = (xx - W/2) / (W/2)
    dy = (yy - H/2) / (H/2)
    vignette = np.clip(1.0 - 0.45 * (dx**2 + dy**2), 0.0, 1.0)[:, :, None]
    base = base * vignette
    base = np.clip(base, 0, 255).astype(np.uint8)

    rgba = np.zeros((H, W, 4), dtype=np.uint8)
    rgba[:, :, :3] = base
    rgba[:, :, 3] = 255
    return Image.fromarray(rgba, 'RGBA')

def render_art(bg, draw_fn, glow_blur=9):
    """Draws illustration with volumetric glow layer + crisp foreground layer."""
    # 1. Glow layer
    glow_surf = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_surf)
    draw_fn(glow_draw, is_glow=True)
    blurred_glow = glow_surf.filter(ImageFilter.GaussianBlur(glow_blur))

    # 2. Main foreground layer
    main_surf = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    main_draw = ImageDraw.Draw(main_surf)
    draw_fn(main_draw, is_glow=False)

    # 3. Composite
    res = Image.alpha_composite(bg, blurred_glow)
    res = Image.alpha_composite(res, main_surf)
    return res

# ==============================================================================
# Drawing Primitives
# ==============================================================================

def draw_sword(draw, tip, pommel, blade_w=8, guard_w=24, is_glow=False, blade_col=(220, 230, 245), glow_col=(180, 210, 255)):
    dx = tip[0] - pommel[0]
    dy = tip[1] - pommel[1]
    length = math.hypot(dx, dy)
    if length < 1: return
    ux = dx / length
    uy = dy / length
    nx = -uy
    ny = ux

    guard_pos = (pommel[0] + ux * (length * 0.28), pommel[1] + uy * (length * 0.28))
    hilt_end = pommel

    if is_glow:
        draw.line([guard_pos, tip], fill=(*glow_col, 200), width=blade_w + 10)
        draw.circle(tip, 8, fill=(*glow_col, 220))
        return

    p_tip = tip
    p_bl_left = (guard_pos[0] + nx * blade_w, guard_pos[1] + ny * blade_w)
    p_bl_right = (guard_pos[0] - nx * blade_w, guard_pos[1] - ny * blade_w)
    draw.polygon([p_tip, p_bl_left, p_bl_right], fill=blade_col)
    draw.line([guard_pos, (tip[0] - ux * 8, tip[1] - uy * 8)], fill=(120, 130, 150), width=2)
    draw.line([p_bl_left, p_tip], fill=(255, 255, 255), width=1)

    g_left = (guard_pos[0] + nx * guard_w, guard_pos[1] + ny * guard_w)
    g_right = (guard_pos[0] - nx * guard_w, guard_pos[1] - ny * guard_w)
    draw.line([g_left, g_right], fill=(210, 175, 80), width=4)
    draw.circle(g_left, 3, fill=(240, 210, 110))
    draw.circle(g_right, 3, fill=(240, 210, 110))
    draw.line([hilt_end, guard_pos], fill=(90, 50, 40), width=4)
    draw.circle(hilt_end, 5, fill=(210, 175, 80))

def draw_dagger(draw, tip, pommel, blade_w=5, guard_w=14, is_glow=False, blade_col=(210, 225, 235), glow_col=(100, 240, 160)):
    dx = tip[0] - pommel[0]
    dy = tip[1] - pommel[1]
    length = math.hypot(dx, dy)
    if length < 1: return
    ux = dx / length
    uy = dy / length
    nx = -uy
    ny = ux

    guard_pos = (pommel[0] + ux * (length * 0.32), pommel[1] + uy * (length * 0.32))

    if is_glow:
        draw.line([guard_pos, tip], fill=(*glow_col, 200), width=blade_w + 8)
        return

    p_bl_left = (guard_pos[0] + nx * blade_w, guard_pos[1] + ny * blade_w)
    p_bl_right = (guard_pos[0] - nx * blade_w, guard_pos[1] - ny * blade_w)
    draw.polygon([tip, p_bl_left, p_bl_right], fill=blade_col)
    draw.line([guard_pos, tip], fill=(255, 255, 255), width=1)
    draw.line([(guard_pos[0] + nx * guard_w, guard_pos[1] + ny * guard_w),
               (guard_pos[0] - nx * guard_w, guard_pos[1] - ny * guard_w)],
              fill=(160, 160, 170), width=3)
    draw.line([pommel, guard_pos], fill=(40, 40, 50), width=3)
    draw.circle(pommel, 3, fill=(180, 180, 190))

def draw_shield_shape(draw, cx, cy, w, h, is_glow=False, fill_col=(40, 60, 100), trim_col=(215, 180, 75), glow_col=(100, 160, 255)):
    top = cy - h // 2
    bot = cy + h // 2
    left = cx - w // 2
    right = cx + w // 2
    mid_y = cy + h // 8

    pts = [
        (left, top),
        (right, top),
        (right, mid_y),
        (cx, bot),
        (left, mid_y)
    ]

    if is_glow:
        draw.polygon(pts, fill=(*glow_col, 160))
        return

    draw.polygon(pts, fill=fill_col)
    draw.polygon(pts, outline=trim_col, width=3)
    in_pts = [
        (left + 5, top + 4),
        (right - 5, top + 4),
        (right - 5, mid_y - 2),
        (cx, bot - 7),
        (left + 5, mid_y - 2)
    ]
    draw.polygon(in_pts, outline=(trim_col[0]//2, trim_col[1]//2, trim_col[2]//2), width=1)

def draw_skull_shape(draw, cx, cy, r=18, is_glow=False, skull_col=(220, 215, 210), eye_col=(30, 20, 30), glow_col=(180, 60, 60)):
    if is_glow:
        draw.circle((cx, cy - 2), r + 8, fill=(*glow_col, 180))
        return

    draw.circle((cx, cy - 4), r, fill=skull_col)
    draw.rectangle([cx - r * 0.55, cy - 2, cx + r * 0.55, cy + r * 0.75], fill=skull_col)
    draw.circle((cx - r * 0.38, cy - 3), r * 0.28, fill=eye_col)
    draw.circle((cx + r * 0.38, cy - 3), r * 0.28, fill=eye_col)
    draw.polygon([(cx, cy + 2), (cx - 2, cy + 5), (cx + 2, cy + 5)], fill=eye_col)
    for i in [-4, 0, 4]:
        draw.line([(cx + i, cy + r * 0.45), (cx + i, cy + r * 0.75)], fill=eye_col, width=1)

def draw_flask_shape(draw, cx, cy, w=32, h=44, is_glow=False, liquid_col=(60, 220, 110), glow_col=(50, 255, 100)):
    neck_w = w * 0.35
    neck_h = h * 0.3
    body_h = h * 0.7
    top = cy - h // 2
    bot = cy + h // 2

    pts = [
        (cx - neck_w/2, top),
        (cx + neck_w/2, top),
        (cx + neck_w/2, top + neck_h),
        (cx + w/2, bot),
        (cx - w/2, bot),
        (cx - neck_w/2, top + neck_h)
    ]

    if is_glow:
        draw.polygon(pts, fill=(*glow_col, 180))
        return

    draw.polygon(pts, fill=(20, 30, 35, 180), outline=(150, 180, 190), width=2)
    # Liquid
    liq_pts = [
        (cx - w*0.4, cy + h*0.05),
        (cx + w*0.4, cy + h*0.05),
        (cx + w/2 - 2, bot - 2),
        (cx - w/2 + 2, bot - 2)
    ]
    draw.polygon(liq_pts, fill=liquid_col)
    # Cork
    draw.rectangle([cx - neck_w*0.6, top - 6, cx + neck_w*0.6, top], fill=(160, 100, 60))
    # Bubbles
    draw.circle((cx - 4, cy + h*0.25), 3, fill=(200, 255, 210))
    draw.circle((cx + 5, cy + h*0.15), 2, fill=(200, 255, 210))

def draw_spark_star(draw, pt, radius=12, col=(255, 255, 255)):
    px, py = pt
    draw.line([(px - radius, py), (px + radius, py)], fill=col, width=2)
    draw.line([(px, py - radius), (px, py + radius)], fill=col, width=2)
    d = int(radius * 0.6)
    draw.line([(px - d, py - d), (px + d, py + d)], fill=col, width=1)
    draw.line([(px + d, py - d), (px - d, py + d)], fill=col, width=1)
    draw.circle(pt, 2, fill=(255, 255, 255))

def draw_lightning_bolt(draw, start, end, is_glow=False, bolt_col=(180, 240, 255), glow_col=(50, 180, 255), width=3, seed=42):
    rng = random.Random(seed)
    pts = [start]
    steps = 6
    dx = (end[0] - start[0]) / steps
    dy = (end[1] - start[1]) / steps
    nx = -dy
    ny = dx
    norm = math.hypot(nx, ny)
    if norm > 0:
        nx /= norm
        ny /= norm

    cur = list(start)
    for i in range(1, steps):
        cur[0] += dx
        cur[1] += dy
        jitter = rng.uniform(-14, 14)
        pts.append((cur[0] + nx * jitter, cur[1] + ny * jitter))
    pts.append(end)

    if is_glow:
        draw.line(pts, fill=(*glow_col, 200), width=width + 8)
        return
    draw.line(pts, fill=bolt_col, width=width)
    draw.line(pts, fill=(255, 255, 255), width=max(1, width - 2))

# ==============================================================================
# Card Artist Definitions (All 84 Cards)
# ==============================================================================

CARD_ARTISTS = {}

def register(card_id):
    def decorator(fn):
        CARD_ARTISTS[card_id] = fn
        return fn
    return decorator

# ----------------- ATTACKS (Warrior / Red) -----------------

@register("strike")
def art_strike(draw, is_glow):
    draw_sword(draw, (200, 28), (60, 108), blade_w=9, is_glow=is_glow)
    if is_glow:
        draw.arc([70, 15, 220, 115], start=-140, end=-20, fill=(255, 200, 180, 180), width=12)
    else:
        draw.arc([70, 15, 220, 115], start=-140, end=-20, fill=(255, 255, 255), width=3)
        draw_spark_star(draw, (185, 42), radius=14, col=(255, 240, 200))

@register("bash")
def art_bash(draw, is_glow):
    head = (165, 42)
    butt = (65, 105)
    if is_glow:
        draw.line([butt, head], fill=(255, 140, 50, 160), width=16)
        draw.rectangle([head[0]-22, head[1]-18, head[0]+22, head[1]+18], fill=(255, 100, 40, 220))
    else:
        draw.line([butt, head], fill=(120, 75, 45), width=6)
        draw.rectangle([head[0]-20, head[1]-16, head[0]+20, head[1]+16], fill=(160, 165, 175), outline=(220, 225, 235), width=2)
        draw.polygon([(head[0]-20, head[1]-8), (head[0]-30, head[1]), (head[0]-20, head[1]+8)], fill=(200, 205, 215))
        draw.polygon([(head[0]+20, head[1]-8), (head[0]+30, head[1]), (head[0]+20, head[1]+8)], fill=(200, 205, 215))
        draw_spark_star(draw, (135, 42), radius=16, col=(255, 220, 100))

@register("cleave")
def art_cleave(draw, is_glow):
    if is_glow:
        draw.arc([30, -10, 230, 140], start=-15, end=195, fill=(255, 60, 60, 220), width=18)
    else:
        draw.arc([30, -10, 230, 140], start=-15, end=195, fill=(255, 120, 120), width=6)
        draw.arc([35, -5, 225, 135], start=-10, end=190, fill=(255, 255, 255), width=2)
        draw_spark_star(draw, (70, 75), radius=10, col=(255, 200, 200))
        draw_spark_star(draw, (190, 75), radius=10, col=(255, 200, 200))

@register("heavy_blade")
def art_heavy_blade(draw, is_glow):
    tip = (130, 115)
    pommel = (130, 15)
    if is_glow:
        draw.line([pommel, tip], fill=(255, 80, 80, 200), width=28)
    else:
        draw_sword(draw, tip, pommel, blade_w=16, guard_w=34, is_glow=False, blade_col=(180, 190, 205))
        # Red runic inscription
        draw.line([(130, 50), (130, 95)], fill=(255, 50, 50), width=3)
        draw_spark_star(draw, (130, 112), radius=12, col=(255, 100, 100))

@register("clash")
def art_clash(draw, is_glow):
    draw_sword(draw, (190, 35), (70, 105), blade_w=8, guard_w=20, is_glow=is_glow, glow_col=(255, 160, 60))
    draw_sword(draw, (70, 35), (190, 105), blade_w=8, guard_w=20, is_glow=is_glow, glow_col=(255, 160, 60))
    if not is_glow:
        draw_spark_star(draw, (130, 65), radius=22, col=(255, 255, 230))

@register("iron_wave")
def art_iron_wave(draw, is_glow):
    draw_shield_shape(draw, 75, 55, 42, 54, is_glow=is_glow, fill_col=(70, 75, 85), trim_col=(170, 175, 185))
    if is_glow:
        draw.line([(95, 95), (230, 95)], fill=(255, 170, 60, 200), width=12)
    else:
        # Jagged earth spike wave
        pts = [(95, 95), (115, 65), (130, 95), (155, 50), (175, 95), (200, 40), (225, 95)]
        draw.polygon(pts, fill=(130, 110, 95), outline=(210, 185, 150), width=2)
        draw_spark_star(draw, (200, 40), radius=12, col=(255, 220, 140))

@register("whirlwind")
def art_whirlwind(draw, is_glow):
    if is_glow:
        for r in [25, 42, 58]:
            draw.arc([130-r, 64-r//2, 130+r, 64+r//2], start=0, end=360, fill=(255, 180, 100, 150), width=8)
    else:
        for r, deg in [(25, 30), (42, 120), (58, 210)]:
            draw.arc([130-r, 64-r//2, 130+r, 64+r//2], start=deg, end=deg+160, fill=(255, 230, 180), width=2)
        draw_sword(draw, (175, 50), (85, 78), blade_w=6, guard_w=16, is_glow=False)

@register("feed")
def art_feed(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.ellipse([cx-45, cy-35, cx+45, cy+35], fill=(230, 20, 20, 200))
    else:
        # Demonic gaping maw
        draw.ellipse([cx-40, cy-30, cx+40, cy+30], fill=(20, 5, 8), outline=(180, 30, 30), width=3)
        # Upper fangs
        for x in [-26, -10, 6, 22]:
            draw.polygon([(cx+x, cy-22), (cx+x+5, cy-6), (cx+x+10, cy-22)], fill=(245, 235, 220))
        # Lower fangs
        for x in [-20, -4, 12]:
            draw.polygon([(cx+x, cy+22), (cx+x+5, cy+6), (cx+x+10, cy+22)], fill=(245, 235, 220))
        # Crimson core drool
        draw.line([(cx, cy-4), (cx, cy+18)], fill=(255, 40, 40), width=3)

@register("anger")
def art_anger(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw_skull_shape(draw, cx, cy+4, r=22, is_glow=True, glow_col=(255, 60, 20))
        draw.arc([cx-40, cy-35, cx+40, cy+45], start=180, end=360, fill=(255, 160, 40, 220), width=20)
    else:
        # Flaming horns / aura
        draw.polygon([(cx-18, cy-12), (cx-32, cy-38), (cx-10, cy-20)], fill=(255, 120, 20))
        draw.polygon([(cx+18, cy-12), (cx+32, cy-38), (cx+10, cy-20)], fill=(255, 120, 20))
        draw_skull_shape(draw, cx, cy+4, r=20, is_glow=False, skull_col=(235, 220, 210), eye_col=(255, 40, 20))

@register("blood_for_blood")
def art_blood_for_blood(draw, is_glow):
    draw_dagger(draw, (170, 35), (80, 95), blade_w=8, guard_w=18, is_glow=is_glow, blade_col=(140, 40, 40), glow_col=(255, 20, 20))
    if not is_glow:
        # Dripping blood drops
        for pt, r in [((155, 65), 5), ((145, 85), 4), ((135, 105), 3)]:
            draw.circle(pt, r, fill=(220, 20, 30))
            draw.polygon([(pt[0]-r, pt[1]), (pt[0], pt[1]-r*1.8), (pt[0]+r, pt[1])], fill=(220, 20, 30))

@register("fiend_fire")
def art_fiend_fire(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.ellipse([cx-50, cy-40, cx+50, cy+45], fill=(255, 70, 20, 220))
    else:
        # Flame tongues
        for ox, h, col in [(-25, 45, (255, 60, 20)), (25, 45, (255, 60, 20)), (0, 60, (255, 180, 40))]:
            draw.polygon([(cx+ox-18, cy+35), (cx+ox, cy+35-h), (cx+ox+18, cy+35)], fill=col)
        draw.circle((cx, cy+15), 18, fill=(255, 240, 150))
        draw_spark_star(draw, (cx, cy-10), radius=14, col=(255, 255, 255))

@register("omnislash")
def art_omnislash(draw, is_glow):
    slashes = [
        ((35, 20), (225, 108)),
        ((35, 108), (225, 20)),
        ((70, 15), (190, 115)),
        ((25, 64), (235, 64))
    ]
    if is_glow:
        for p1, p2 in slashes:
            draw.line([p1, p2], fill=(120, 220, 255, 180), width=8)
    else:
        for p1, p2 in slashes:
            draw.line([p1, p2], fill=(255, 255, 255), width=2)
        draw_spark_star(draw, CENTER, radius=18, col=(220, 250, 255))

# ----------------- SHADOW ASSASSIN / ROGUE (Green & Daggers) -----------------

@register("shiv")
def art_shiv(draw, is_glow):
    draw_dagger(draw, (185, 36), (75, 92), blade_w=6, guard_w=14, is_glow=is_glow, blade_col=(220, 235, 240), glow_col=(70, 230, 150))
    if not is_glow:
        draw_spark_star(draw, (185, 36), radius=12, col=(180, 255, 220))

@register("blade_dance")
def art_blade_dance(draw, is_glow):
    cx, cy = CENTER
    angles = [-60, -30, 0, 30, 60]
    for ang in angles:
        rad = math.radians(ang - 90)
        tip = (cx + math.cos(rad) * 45, cy + math.sin(rad) * 45)
        pommel = (cx + math.cos(rad) * 12, cy + math.sin(rad) * 12)
        draw_dagger(draw, tip, pommel, blade_w=4, guard_w=10, is_glow=is_glow, glow_col=(50, 220, 140))
    if not is_glow:
        draw.arc([cx-48, cy-48, cx+48, cy+48], start=-140, end=-40, fill=(120, 255, 180), width=2)

@register("finisher")
def art_finisher(draw, is_glow):
    draw_dagger(draw, (170, 35), (85, 95), blade_w=6, guard_w=16, is_glow=is_glow, glow_col=(255, 90, 90))
    draw_dagger(draw, (90, 35), (175, 95), blade_w=6, guard_w=16, is_glow=is_glow, glow_col=(255, 90, 90))
    if not is_glow:
        draw_spark_star(draw, CENTER, radius=18, col=(255, 255, 200))

@register("neutralize")
def art_neutralize(draw, is_glow):
    draw_dagger(draw, (180, 42), (80, 86), blade_w=6, guard_w=14, is_glow=is_glow, glow_col=(40, 240, 120))
    if not is_glow:
        # Emerald poison drop falling from tip
        drop_pos = (185, 62)
        draw.circle(drop_pos, 4, fill=(40, 255, 100))
        draw.polygon([(drop_pos[0]-4, drop_pos[1]), (drop_pos[0], drop_pos[1]-7), (drop_pos[0]+4, drop_pos[1])], fill=(40, 255, 100))

@register("gouge")
def art_gouge(draw, is_glow):
    claws = [
        ((70, 25), (150, 105)),
        ((105, 20), (185, 100)),
        ((140, 25), (220, 105))
    ]
    if is_glow:
        for p1, p2 in claws:
            draw.line([p1, p2], fill=(255, 40, 40, 200), width=10)
    else:
        for p1, p2 in claws:
            draw.line([p1, p2], fill=(255, 70, 70), width=4)
            draw.line([p1, p2], fill=(255, 240, 240), width=1)

@register("deadly_poison")
def art_deadly_poison(draw, is_glow):
    draw_flask_shape(draw, CENTER[0], CENTER[1]+6, w=38, h=52, is_glow=is_glow, liquid_col=(50, 240, 100), glow_col=(40, 255, 90))
    if not is_glow:
        # Rising skull vapor
        draw_skull_shape(draw, CENTER[0], CENTER[1]-34, r=10, is_glow=False, skull_col=(100, 220, 130), eye_col=(20, 40, 25))

@register("bouncing_flask")
def art_bouncing_flask(draw, is_glow):
    draw_flask_shape(draw, 100, 68, w=34, h=46, is_glow=is_glow, liquid_col=(60, 230, 90), glow_col=(60, 240, 100))
    if is_glow:
        draw.arc([90, 25, 210, 110], start=-140, end=-20, fill=(80, 255, 120, 180), width=10)
    else:
        draw.arc([90, 25, 210, 110], start=-140, end=-20, fill=(120, 255, 160), width=3)
        for pt in [(160, 40), (180, 48), (200, 65)]:
            draw.circle(pt, 4, fill=(80, 255, 110))

@register("crippling_cloud")
def art_crippling_cloud(draw, is_glow):
    cx, cy = CENTER
    puffs = [
        (cx-45, cy, 28), (cx, cy-12, 36), (cx+45, cy+2, 30),
        (cx-20, cy+14, 25), (cx+25, cy+16, 26)
    ]
    if is_glow:
        for x, y, r in puffs:
            draw.circle((x, y), r+6, fill=(80, 220, 90, 140))
    else:
        for x, y, r in puffs:
            draw.circle((x, y), r, fill=(40, 130, 65, 210))
        draw_skull_shape(draw, cx, cy-4, r=13, is_glow=False, skull_col=(120, 220, 150), eye_col=(15, 45, 20))

@register("corpse_explosion")
def art_corpse_explosion(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.circle((cx, cy), 48, fill=(90, 255, 70, 220))
    else:
        draw_skull_shape(draw, cx, cy, r=22, is_glow=False, skull_col=(180, 215, 170), eye_col=(20, 50, 25))
        # Exploding blast lines
        for ang in range(0, 360, 45):
            rad = math.radians(ang)
            p1 = (cx + math.cos(rad) * 26, cy + math.sin(rad) * 26)
            p2 = (cx + math.cos(rad) * 55, cy + math.sin(rad) * 55)
            draw.line([p1, p2], fill=(80, 255, 100), width=3)
        draw_spark_star(draw, (cx, cy-5), radius=16, col=(220, 255, 200))

@register("catalyst")
def art_catalyst(draw, is_glow):
    cx, cy = CENTER
    r = 34
    pts = [(cx, cy-r), (cx+int(r*0.866), cy+r//2), (cx-int(r*0.866), cy+r//2)]
    if is_glow:
        draw.polygon(pts, fill=(50, 255, 120, 180))
    else:
        draw.polygon(pts, outline=(80, 255, 130), width=3)
        draw.circle((cx, cy+4), 16, outline=(120, 255, 160), width=2)
        draw_spark_star(draw, (cx, cy+4), radius=10, col=(200, 255, 210))
        draw_flask_shape(draw, cx, cy+4, w=18, h=24, is_glow=False)

@register("envenom")
def art_envenom(draw, is_glow):
    draw_dagger(draw, (180, 35), (80, 95), blade_w=7, guard_w=16, is_glow=is_glow, glow_col=(50, 240, 80))
    if not is_glow:
        # Serpent coiled around blade
        draw.arc([105, 45, 145, 85], start=-30, end=150, fill=(35, 190, 70), width=5)
        draw.arc([130, 35, 170, 75], start=-30, end=150, fill=(35, 190, 70), width=5)
        # Viper eye
        draw.circle((165, 44), 3, fill=(255, 220, 40))

@register("noxious_fumes")
def art_noxious_fumes(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.rectangle([cx-25, cy+15, cx+25, cy+45], fill=(40, 230, 90, 180))
        draw.arc([cx-45, cy-45, cx+45, cy+25], start=0, end=360, fill=(70, 255, 100, 160), width=20)
    else:
        # Censer bowl
        draw.polygon([(cx-25, cy+18), (cx+25, cy+18), (cx+18, cy+45), (cx-18, cy+45)], fill=(80, 85, 95), outline=(160, 165, 175), width=2)
        # Smoke fumes
        for ox in [-15, 0, 15]:
            draw.arc([cx+ox-20, cy-35, cx+ox+20, cy+15], start=-140, end=40, fill=(70, 220, 100), width=3)
        draw_skull_shape(draw, cx, cy-22, r=10, is_glow=False, skull_col=(100, 240, 130), eye_col=(15, 40, 20))

@register("cloak_and_dagger")
def art_cloak_and_dagger(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.polygon([(cx-35, cy-25), (cx+35, cy-25), (cx+48, cy+45), (cx-48, cy+45)], fill=(30, 180, 100, 160))
    else:
        # Hood
        draw.polygon([(cx, cy-36), (cx+32, cy+38), (cx-32, cy+38)], fill=(25, 30, 38))
        # Deep face shadow
        draw.polygon([(cx, cy-20), (cx+18, cy+18), (cx-18, cy+18)], fill=(10, 12, 16))
        # Glowing rogue eyes
        draw.ellipse([cx-10, cy-2, cx-4, cy+2], fill=(60, 255, 120))
        draw.ellipse([cx+4, cy-2, cx+10, cy+2], fill=(60, 255, 120))
        # Dagger in foreground
        draw_dagger(draw, (cx+48, cy-10), (cx+28, cy+40), blade_w=5, guard_w=12, is_glow=False)

@register("backflip")
def art_backflip(draw, is_glow):
    if is_glow:
        draw.arc([50, 15, 210, 115], start=40, end=240, fill=(70, 240, 140, 180), width=14)
    else:
        draw.arc([50, 15, 210, 115], start=40, end=240, fill=(120, 255, 170), width=4)
        cx, cy = CENTER
        # Silhouetted acrobat
        draw.circle((cx-12, cy-18), 8, fill=(220, 230, 240))
        draw.line([(cx-12, cy-18), (cx+8, cy-2)], fill=(200, 210, 220), width=5)
        draw.line([(cx+8, cy-2), (cx+24, cy-14)], fill=(200, 210, 220), width=4)
        draw_spark_star(draw, (cx+24, cy-14), radius=10, col=(255, 255, 255))

@register("shadowstep")
def art_shadowstep(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.ellipse([cx-40, cy-25, cx+40, cy+25], fill=(130, 50, 220, 180))
    else:
        draw.ellipse([cx-35, cy-20, cx+35, cy+20], fill=(15, 10, 25), outline=(150, 70, 240), width=3)
        # Footprint silhouettes
        for ox, oy in [(-20, 4), (0, -4), (20, 4)]:
            draw.ellipse([cx+ox-6, cy+oy-10, cx+ox+6, cy+oy+10], fill=(180, 130, 240))
        draw_spark_star(draw, (cx+20, cy+4), radius=8, col=(220, 190, 255))

@register("footwork")
def art_footwork(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.arc([cx-50, cy-30, cx+50, cy+40], start=-30, end=190, fill=(80, 240, 130, 160), width=12)
    else:
        # Agile boots
        draw.polygon([(cx-30, cy+10), (cx-10, cy+10), (cx-5, cy+30), (cx-35, cy+30)], fill=(70, 80, 95))
        draw.polygon([(cx+10, cy-15), (cx+30, cy-15), (cx+35, cy+8), (cx+5, cy+8)], fill=(70, 80, 95))
        # Wind trails
        draw.arc([cx-50, cy-30, cx+50, cy+40], start=-30, end=190, fill=(100, 255, 160), width=3)
        draw_spark_star(draw, (cx+35, cy+8), radius=10, col=(200, 255, 220))

@register("infinite_blades")
def art_infinite_blades(draw, is_glow):
    for i, x in enumerate(range(55, 215, 30)):
        tip = (x, 30 + (i % 2) * 10)
        pommel = (x - 10, 100)
        draw_dagger(draw, tip, pommel, blade_w=5, guard_w=12, is_glow=is_glow, glow_col=(70, 220, 150))

@register("accuracy")
def art_accuracy(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.circle((cx, cy), 38, outline=(80, 255, 120, 220), width=8)
    else:
        for r in [14, 26, 38]:
            draw.circle((cx, cy), r, outline=(70, 220, 110), width=2)
        # Crosshair lines
        draw.line([(cx-44, cy), (cx+44, cy)], fill=(120, 255, 150), width=2)
        draw.line([(cx, cy-44), (cx, cy+44)], fill=(120, 255, 150), width=2)
        # Center pinned dagger
        draw_dagger(draw, (cx, cy), (cx+25, cy+35), blade_w=5, guard_w=12, is_glow=False)
        draw_spark_star(draw, (cx, cy), radius=10, col=(255, 255, 255))

@register("burst")
def art_burst(draw, is_glow):
    c1 = (100, 64)
    c2 = (160, 64)
    if is_glow:
        draw.circle(c1, 30, fill=(255, 220, 60, 180))
        draw.circle(c2, 30, fill=(255, 220, 60, 180))
    else:
        draw_spark_star(draw, c1, radius=26, col=(255, 250, 180))
        draw_spark_star(draw, c2, radius=26, col=(255, 250, 180))
        draw.line([(60, 64), (200, 64)], fill=(255, 255, 255), width=2)

@register("double_tap")
def art_double_tap(draw, is_glow):
    if is_glow:
        draw.line([(50, 48), (210, 48)], fill=(255, 160, 40, 200), width=10)
        draw.line([(50, 80), (210, 80)], fill=(255, 160, 40, 200), width=10)
    else:
        # Dual bullets / arrows
        for y in [48, 80]:
            draw.line([(50, y), (180, y)], fill=(255, 200, 90), width=3)
            draw.polygon([(180, y-5), (205, y), (180, y+5)], fill=(255, 245, 180))
            draw_spark_star(draw, (205, y), radius=10, col=(255, 255, 255))

@register("storm_of_steel")
def art_storm_of_steel(draw, is_glow):
    rng = random.Random(123)
    for i in range(12):
        x = rng.uniform(40, 220)
        y = rng.uniform(20, 80)
        tip = (x + 18, y + 26)
        pommel = (x - 12, y - 16)
        draw_dagger(draw, tip, pommel, blade_w=4, guard_w=10, is_glow=is_glow, glow_col=(100, 220, 160))

@register("terror")
def art_terror(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.ellipse([cx-40, cy-35, cx+40, cy+35], fill=(160, 40, 40, 180))
    else:
        # Nightmare phantom face
        draw.ellipse([cx-36, cy-30, cx+36, cy+30], fill=(20, 10, 15), outline=(180, 40, 50), width=2)
        # Gaping terror eyes & mouth
        draw.ellipse([cx-18, cy-14, cx-6, cy+2], fill=(255, 50, 50))
        draw.ellipse([cx+6, cy-14, cx+18, cy+2], fill=(255, 50, 50))
        draw.ellipse([cx-14, cy+8, cx+14, cy+25], fill=(255, 30, 30))

@register("malaise")
def art_malaise(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.circle((cx, cy), 36, fill=(150, 40, 200, 160))
    else:
        # Weeping soul silhouette
        draw.circle((cx, cy-10), 14, fill=(18, 14, 25), outline=(160, 60, 220), width=2)
        draw.ellipse([cx-22, cy+4, cx+22, cy+34], fill=(18, 14, 25), outline=(160, 60, 220), width=2)
        # Binding chains
        draw.line([(cx-38, cy-15), (cx+38, cy+25)], fill=(130, 135, 150), width=3)
        draw.line([(cx+38, cy-15), (cx-38, cy+25)], fill=(130, 135, 150), width=3)

@register("wraith_form")
def art_wraith_form(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.ellipse([cx-35, cy-40, cx+35, cy+45], fill=(40, 240, 200, 180))
    else:
        # Ethereal floating wraith
        pts = [
            (cx, cy-38), (cx+28, cy-10), (cx+34, cy+25),
            (cx+15, cy+42), (cx, cy+30), (cx-15, cy+42),
            (cx-34, cy+25), (cx-28, cy-10)
        ]
        draw.polygon(pts, fill=(20, 50, 55, 220), outline=(60, 230, 200), width=2)
        # Luminous soul eyes
        draw.circle((cx-10, cy-12), 4, fill=(100, 255, 230))
        draw.circle((cx+10, cy-12), 4, fill=(100, 255, 230))
        draw_spark_star(draw, (cx-10, cy-12), radius=8, col=(255, 255, 255))
        draw_spark_star(draw, (cx+10, cy-12), radius=8, col=(255, 255, 255))

# ----------------- SHIELDS & DEFENSE (Blue & Steel) -----------------

@register("defend")
def art_defend(draw, is_glow):
    draw_shield_shape(draw, CENTER[0], CENTER[1], 54, 68, is_glow=is_glow, fill_col=(45, 65, 105), trim_col=(215, 185, 75))
    if not is_glow:
        # Central boss
        draw.circle(CENTER, 10, fill=(190, 200, 215), outline=(230, 200, 90), width=2)
        draw_spark_star(draw, CENTER, radius=8, col=(255, 255, 255))

@register("armaments")
def art_armaments(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.rectangle([cx-35, cy+5, cx+35, cy+35], fill=(255, 140, 40, 180))
    else:
        # Anvil
        draw.polygon([(cx-40, cy+10), (cx+40, cy+10), (cx+25, cy+35), (cx-25, cy+35)], fill=(80, 85, 95), outline=(170, 175, 185), width=2)
        # Glowing hot steel
        draw.rectangle([cx-15, cy+5, cx+15, cy+12], fill=(255, 180, 50))
        # Forge hammer striking
        draw.line([(cx+10, cy-35), (cx-8, cy+5)], fill=(120, 75, 45), width=5)
        draw.rectangle([cx-16, cy-2, cx+2, cy+10], fill=(160, 165, 175))
        draw_spark_star(draw, (cx-6, cy+6), radius=14, col=(255, 255, 200))

@register("entrench")
def art_entrench(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.rectangle([cx-55, cy-15, cx+55, cy+35], fill=(100, 160, 240, 160))
    else:
        # Stone battlement
        draw.rectangle([cx-50, cy-5, cx+50, cy+35], fill=(70, 75, 85), outline=(160, 165, 180), width=2)
        # Crenellations
        for x in [-45, -15, 15, 35]:
            draw.rectangle([cx+x, cy-18, cx+x+14, cy-5], fill=(70, 75, 85), outline=(160, 165, 180), width=2)
        draw_spark_star(draw, (cx, cy-5), radius=12, col=(200, 230, 255))

@register("flame_barrier")
def art_flame_barrier(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.circle((cx, cy), 42, fill=(255, 90, 20, 220))
    else:
        # Ring of fire
        for ang in range(0, 360, 30):
            rad = math.radians(ang)
            px = cx + math.cos(rad) * 36
            py = cy + math.sin(rad) * 36
            draw.circle((px, py), 10, fill=(255, 140, 30))
        draw_shield_shape(draw, cx, cy, 44, 54, is_glow=False, fill_col=(90, 35, 25), trim_col=(255, 200, 80))
        draw_spark_star(draw, (cx, cy), radius=12, col=(255, 240, 180))

@register("impervious")
def art_impervious(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.polygon([(cx, cy-42), (cx+42, cy), (cx, cy+42), (cx-42, cy)], fill=(120, 220, 255, 220))
    else:
        draw_shield_shape(draw, cx, cy, 60, 74, is_glow=False, fill_col=(50, 120, 180), trim_col=(255, 255, 255))
        # Diamond facets
        draw.polygon([(cx, cy-32), (cx+26, cy), (cx, cy+32), (cx-26, cy)], outline=(220, 245, 255), width=2)
        draw_spark_star(draw, (cx, cy-32), radius=14, col=(255, 255, 255))

@register("barricade")
def art_barricade(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.rectangle([cx-45, cy-35, cx+45, cy+35], fill=(210, 160, 60, 160))
    else:
        # Iron gate
        draw.rectangle([cx-40, cy-32, cx+40, cy+32], fill=(50, 45, 42), outline=(190, 150, 70), width=3)
        # Crossed iron bars
        draw.line([(cx-40, cy-32), (cx+40, cy+32)], fill=(140, 145, 155), width=4)
        draw.line([(cx+40, cy-32), (cx-40, cy+32)], fill=(140, 145, 155), width=4)
        # Heavy padlock
        draw.circle((cx, cy), 12, fill=(215, 180, 75))
        draw.circle((cx, cy), 4, fill=(30, 20, 15))

@register("body_slam")
def art_body_slam(draw, is_glow):
    draw_shield_shape(draw, 150, 64, 52, 66, is_glow=is_glow, fill_col=(70, 75, 85), trim_col=(220, 100, 60), glow_col=(255, 120, 40))
    if not is_glow:
        # Kinetic impact shock lines
        for y in [40, 64, 88]:
            draw.line([(60, y), (115, y)], fill=(255, 180, 80), width=4)
            draw_spark_star(draw, (115, y), radius=8, col=(255, 240, 180))

@register("true_grit")
def art_true_grit(draw, is_glow):
    cx, cy = CENTER
    draw_shield_shape(draw, cx, cy, 54, 68, is_glow=is_glow, fill_col=(55, 60, 70), trim_col=(180, 185, 195))
    if not is_glow:
        # Battle scars
        draw.line([(cx-18, cy-15), (cx+14, cy+18)], fill=(30, 32, 38), width=3)
        draw.line([(cx+10, cy-20), (cx-12, cy+5)], fill=(30, 32, 38), width=2)
        # Embedded arrow
        draw.line([(cx-32, cy+5), (cx-5, cy+10)], fill=(120, 80, 50), width=3)
        draw.polygon([(cx-5, cy+7), (cx, cy+10), (cx-5, cy+13)], fill=(160, 165, 175))

@register("holy_shield")
def art_holy_shield(draw, is_glow):
    cx, cy = CENTER
    draw_shield_shape(draw, cx, cy, 56, 72, is_glow=is_glow, fill_col=(210, 175, 60), trim_col=(255, 240, 160), glow_col=(255, 215, 80))
    if not is_glow:
        # Radiant golden cross
        draw.line([(cx, cy-22), (cx, cy+22)], fill=(255, 255, 255), width=4)
        draw.line([(cx-16, cy-8), (cx+16, cy-8)], fill=(255, 255, 255), width=4)
        draw_spark_star(draw, (cx, cy-8), radius=12, col=(255, 255, 230))

@register("frost_barrier")
def art_frost_barrier(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.circle((cx, cy), 42, fill=(100, 220, 255, 200))
    else:
        # Ice crystal cluster
        for ang in range(0, 360, 60):
            rad = math.radians(ang)
            px = cx + math.cos(rad) * 28
            py = cy + math.sin(rad) * 28
            draw.polygon([(cx, cy), (px-6, py), (px, py-10), (px+6, py)], fill=(180, 240, 255), outline=(255, 255, 255), width=1)
        draw.circle((cx, cy), 14, fill=(120, 210, 245), outline=(255, 255, 255), width=2)
        draw_spark_star(draw, (cx, cy), radius=14, col=(255, 255, 255))

@register("glacier")
def art_glacier(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.polygon([(cx-55, cy+38), (cx, cy-45), (cx+55, cy+38)], fill=(90, 210, 255, 200))
    else:
        # Colossal glacial peak
        draw.polygon([(cx-50, cy+35), (cx, cy-40), (cx+50, cy+35)], fill=(110, 195, 240), outline=(220, 245, 255), width=2)
        draw.polygon([(cx-15, cy+35), (cx, cy-40), (cx+50, cy+35)], fill=(160, 225, 255))
        draw_spark_star(draw, (cx, cy-40), radius=14, col=(255, 255, 255))

# ----------------- TEMPEST & LIGHTNING (Electric Cyan & Ice) -----------------

@register("zap")
def art_zap(draw, is_glow):
    draw_lightning_bolt(draw, (55, 85), (205, 45), is_glow=is_glow, bolt_col=(200, 245, 255), glow_col=(50, 190, 255), width=4, seed=11)
    if not is_glow:
        draw_spark_star(draw, (205, 45), radius=14, col=(255, 255, 255))

@register("ball_lightning")
def art_ball_lightning(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.circle((cx, cy), 38, fill=(60, 190, 255, 220))
    else:
        draw.circle((cx, cy), 24, fill=(160, 235, 255), outline=(255, 255, 255), width=2)
        # Orbiting plasma rings
        draw.arc([cx-36, cy-18, cx+36, cy+18], start=0, end=360, fill=(70, 220, 255), width=3)
        draw_spark_star(draw, (cx, cy), radius=16, col=(255, 255, 255))

@register("chain_lightning")
def art_chain_lightning(draw, is_glow):
    draw_lightning_bolt(draw, (45, 25), (130, 65), is_glow=is_glow, width=4, seed=3)
    draw_lightning_bolt(draw, (130, 65), (215, 35), is_glow=is_glow, width=3, seed=7)
    draw_lightning_bolt(draw, (130, 65), (215, 105), is_glow=is_glow, width=3, seed=9)
    if not is_glow:
        draw_spark_star(draw, (130, 65), radius=14, col=(255, 255, 255))

@register("thunder_strike")
def art_thunder_strike(draw, is_glow):
    draw_lightning_bolt(draw, (130, 15), (130, 115), is_glow=is_glow, width=6, seed=99)
    if not is_glow:
        draw_spark_star(draw, (130, 112), radius=22, col=(255, 255, 255))
        draw.ellipse([90, 105, 170, 120], outline=(100, 220, 255), width=2)

@register("blizzard")
def art_blizzard(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.arc([cx-55, cy-40, cx+55, cy+40], start=-30, end=210, fill=(100, 220, 255, 180), width=16)
    else:
        draw.arc([cx-55, cy-40, cx+55, cy+40], start=-30, end=210, fill=(180, 240, 255), width=3)
        # Snowflake particles
        for ox, oy in [(-30, -10), (25, -20), (0, 15), (-20, 25), (35, 10)]:
            draw_spark_star(draw, (cx+ox, cy+oy), radius=8, col=(220, 245, 255))

@register("superconductor")
def art_superconductor(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.rectangle([cx-40, cy-18, cx+40, cy+18], fill=(60, 210, 255, 180))
    else:
        # Magnetic coil core
        draw.rectangle([cx-36, cy-12, cx+36, cy+12], fill=(60, 65, 80), outline=(160, 180, 200), width=2)
        # Electric loop rings
        for x in range(cx-30, cx+35, 14):
            draw.arc([x-6, cy-22, x+6, cy+22], start=-90, end=90, fill=(100, 235, 255), width=3)
        draw_spark_star(draw, (cx, cy), radius=12, col=(255, 255, 255))

@register("static_discharge")
def art_static_discharge(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.circle((cx, cy), 35, fill=(70, 200, 255, 200))
    else:
        draw.circle((cx, cy), 16, fill=(180, 230, 255), outline=(255, 255, 255), width=2)
        for ang in range(0, 360, 45):
            rad = math.radians(ang)
            p1 = (cx + math.cos(rad) * 16, cy + math.sin(rad) * 16)
            p2 = (cx + math.cos(rad) * 45, cy + math.sin(rad) * 45)
            draw_lightning_bolt(draw, p1, p2, is_glow=False, width=2, seed=ang)

# ----------------- RADIANT TEMPLAR (Gold, Sun & Holy Light) -----------------

@register("smite")
def art_smite(draw, is_glow):
    cx = CENTER[0]
    if is_glow:
        draw.polygon([(cx-18, 15), (cx+18, 15), (cx+8, 115), (cx-8, 115)], fill=(255, 220, 80, 220))
    else:
        draw.polygon([(cx-12, 15), (cx+12, 15), (cx+4, 115), (cx-4, 115)], fill=(255, 245, 180))
        draw.line([(cx, 15), (cx, 115)], fill=(255, 255, 255), width=3)
        draw_spark_star(draw, (cx, 115), radius=18, col=(255, 255, 255))

@register("consecration")
def art_consecration(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.circle((cx, cy), 42, fill=(255, 215, 60, 200))
    else:
        # Holy Latin Cross
        draw.rectangle([cx-5, cy-32, cx+5, cy+32], fill=(255, 240, 160), outline=(215, 175, 50), width=1)
        draw.rectangle([cx-22, cy-16, cx+22, cy-6], fill=(255, 240, 160), outline=(215, 175, 50), width=1)
        # Radiating sunbeams
        for ang in range(0, 360, 30):
            rad = math.radians(ang)
            draw.line([(cx+math.cos(rad)*24, cy+math.sin(rad)*24), (cx+math.cos(rad)*44, cy+math.sin(rad)*44)], fill=(255, 220, 100), width=2)
        draw_spark_star(draw, (cx, cy-11), radius=14, col=(255, 255, 255))

@register("divine_favor")
def art_divine_favor(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.ellipse([cx-50, cy-30, cx+50, cy+30], fill=(255, 215, 70, 180))
    else:
        # Angel wings
        # Left wing
        draw.polygon([(cx, cy+15), (cx-45, cy-25), (cx-30, cy+10), (cx-15, cy+20)], fill=(250, 240, 210), outline=(215, 180, 80), width=2)
        # Right wing
        draw.polygon([(cx, cy+15), (cx+45, cy-25), (cx+30, cy+10), (cx+15, cy+20)], fill=(250, 240, 210), outline=(215, 180, 80), width=2)
        draw.circle((cx, cy-5), 8, fill=(255, 230, 120))
        draw_spark_star(draw, (cx, cy-5), radius=12, col=(255, 255, 255))

@register("radiant_vow")
def art_radiant_vow(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.rectangle([cx-30, cy-35, cx+30, cy+35], fill=(255, 215, 70, 160))
    else:
        # Sacred scroll
        draw.rectangle([cx-25, cy-30, cx+25, cy+30], fill=(245, 235, 210), outline=(190, 160, 100), width=2)
        # Scroll rolls
        draw.ellipse([cx-28, cy-35, cx+28, cy-25], fill=(230, 215, 180), outline=(190, 160, 100), width=1)
        draw.ellipse([cx-28, cy+25, cx+28, cy+35], fill=(230, 215, 180), outline=(190, 160, 100), width=1)
        # Golden seal & text lines
        draw.circle((cx, cy+12), 6, fill=(200, 40, 40))
        for y in [-15, -7, 1]:
            draw.line([(cx-16, cy+y), (cx+16, cy+y)], fill=(160, 140, 120), width=2)
        draw_spark_star(draw, (cx, cy-15), radius=10, col=(255, 255, 200))

@register("judgment")
def art_judgment(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.rectangle([cx-38, cy-30, cx+38, cy+35], fill=(255, 215, 80, 180))
    else:
        # Balance scale of justice
        draw.line([(cx, cy-28), (cx, cy+28)], fill=(215, 175, 60), width=4)
        draw.line([(cx-32, cy-18), (cx+32, cy-14)], fill=(215, 175, 60), width=3)
        # Pans
        for x, y in [(-32, -18), (32, -14)]:
            draw.line([(cx+x, cy+y), (cx+x-10, cy+y+22)], fill=(180, 150, 60), width=1)
            draw.line([(cx+x, cy+y), (cx+x+10, cy+y+22)], fill=(180, 150, 60), width=1)
            draw.arc([cx+x-12, cy+y+18, cx+x+12, cy+y+28], start=0, end=180, fill=(215, 180, 75), width=2)
        draw_spark_star(draw, (cx, cy-28), radius=12, col=(255, 255, 255))

@register("heavens_fury")
def art_heavens_fury(draw, is_glow):
    draw_sword(draw, (130, 115), (130, 18), blade_w=12, guard_w=28, is_glow=is_glow, blade_col=(255, 250, 220), glow_col=(255, 215, 60))
    if not is_glow:
        # Holy halos
        draw.arc([130-24, 45-12, 130+24, 45+12], start=0, end=360, fill=(255, 220, 90), width=2)
        draw_spark_star(draw, (130, 112), radius=16, col=(255, 255, 255))

@register("apotheosis")
def art_apotheosis(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.circle((cx, cy-4), 38, fill=(255, 220, 80, 220))
    else:
        # Divine celestial crown
        pts = [(cx-34, cy+15), (cx-34, cy-8), (cx-18, cy+5), (cx, cy-22), (cx+18, cy+5), (cx+34, cy-8), (cx+34, cy+15)]
        draw.polygon(pts, fill=(240, 200, 70), outline=(255, 255, 200), width=2)
        # Crown jewels
        for x, y in [(-34, -8), (-18, 5), (0, -22), (18, 5), (34, -8)]:
            draw.circle((cx+x, cy+y), 3, fill=(100, 220, 255))
        draw_spark_star(draw, (cx, cy-22), radius=16, col=(255, 255, 255))

# ----------------- VOID NECROMANCER (Purple, Bone & Souls) -----------------

@register("reaper")
def art_reaper(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.arc([cx-40, cy-40, cx+40, cy+40], start=-140, end=40, fill=(60, 220, 240, 200), width=16)
    else:
        # Scythe staff
        draw.line([(cx-25, cy+38), (cx+25, cy-32)], fill=(90, 60, 45), width=4)
        # Curved scythe blade
        pts = [(cx+25, cy-32), (cx+35, cy-40), (cx-20, cy-40), (cx-35, cy-20), (cx-10, cy-25)]
        draw.polygon(pts, fill=(210, 225, 235), outline=(60, 220, 240), width=2)
        # Floating soul orb
        draw.circle((cx-15, cy+10), 8, fill=(60, 240, 220))
        draw_spark_star(draw, (cx-15, cy+10), radius=10, col=(255, 255, 255))

@register("soul_drain")
def art_soul_drain(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.arc([60, 20, 200, 108], start=-160, end=-20, fill=(50, 220, 240, 200), width=14)
    else:
        for r, deg in [(40, -140), (25, -160)]:
            draw.arc([cx-r, cy-r//2, cx+r, cy+r//2], start=deg, end=deg+140, fill=(100, 245, 235), width=3)
        draw.circle((180, 50), 10, fill=(80, 240, 220))
        draw_spark_star(draw, (180, 50), radius=12, col=(255, 255, 255))

@register("sever_soul")
def art_sever_soul(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.circle((cx, cy), 32, fill=(60, 230, 240, 200))
    else:
        # Severed soul orb halves
        draw.chord([cx-32, cy-24, cx+16, cy+24], start=90, end=270, fill=(70, 230, 220))
        draw.chord([cx-16, cy-24, cx+32, cy+24], start=-90, end=90, fill=(70, 230, 220))
        # Cutting scythe slash
        draw.line([(cx-25, cy-35), (cx+25, cy+35)], fill=(255, 255, 255), width=3)
        draw_spark_star(draw, (cx, cy), radius=16, col=(255, 255, 255))

@register("exhumation")
def art_exhumation(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.rectangle([cx-30, cy-20, cx+30, cy+35], fill=(50, 220, 180, 160))
    else:
        # Grave earth
        draw.ellipse([cx-45, cy+18, cx+45, cy+42], fill=(45, 35, 30))
        # Skeletal hand clawing upward
        draw.line([(cx, cy+25), (cx, cy-8)], fill=(225, 220, 210), width=5)
        # Fingers
        for ox in [-10, -4, 4, 10]:
            draw.line([(cx, cy-8), (cx+ox, cy-24)], fill=(225, 220, 210), width=3)
        draw_spark_star(draw, (cx, cy-24), radius=10, col=(100, 255, 220))

@register("dark_embrace")
def art_dark_embrace(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.circle((cx, cy), 38, fill=(140, 40, 210, 200))
    else:
        draw.circle((cx, cy), 20, fill=(15, 10, 25), outline=(160, 50, 230), width=3)
        # Coiling shadow tentacles
        for ang in range(0, 360, 60):
            rad = math.radians(ang)
            draw.arc([cx-32, cy-32, cx+32, cy+32], start=ang, end=ang+90, fill=(180, 70, 240), width=3)
        draw_spark_star(draw, (cx, cy), radius=12, col=(220, 180, 255))

@register("feel_no_pain")
def art_feel_no_pain(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.circle((cx, cy), 34, fill=(50, 220, 240, 200))
    else:
        # Ribcage
        for y, w in [(-16, 24), (-4, 28), (8, 26), (20, 20)]:
            draw.arc([cx-w, cy+y-6, cx+w, cy+y+6], start=0, end=180, fill=(220, 215, 205), width=3)
        draw.line([(cx, cy-22), (cx, cy+25)], fill=(220, 215, 205), width=4)
        # Soul flame inside chest
        draw.ellipse([cx-10, cy-12, cx+10, cy+12], fill=(60, 240, 220))
        draw_spark_star(draw, (cx, cy), radius=12, col=(255, 255, 255))

@register("corruption")
def art_corruption(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.rectangle([cx-35, cy-25, cx+35, cy+30], fill=(130, 40, 200, 180))
    else:
        # Grimoire
        draw.rectangle([cx-30, cy-22, cx+30, cy+26], fill=(30, 20, 40), outline=(150, 60, 220), width=2)
        # Bleeding dark ichor
        for x in [-15, 0, 15]:
            draw.line([(cx+x, cy-10), (cx+x, cy+20)], fill=(180, 50, 240), width=3)
        draw.circle((cx, cy-2), 8, fill=(20, 10, 30), outline=(180, 50, 240), width=2)
        draw_spark_star(draw, (cx, cy-2), radius=10, col=(220, 180, 255))

@register("hemokinesis")
def art_hemokinesis(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.circle((cx, cy), 35, fill=(230, 20, 40, 220))
    else:
        # Blood orb
        draw.circle((cx, cy), 18, fill=(210, 20, 35), outline=(255, 100, 110), width=2)
        # Spiraling blood ribbons
        draw.arc([cx-34, cy-20, cx+34, cy+20], start=0, end=180, fill=(230, 40, 50), width=3)
        draw.arc([cx-30, cy-28, cx+30, cy+28], start=180, end=360, fill=(230, 40, 50), width=3)
        draw_spark_star(draw, (cx-4, cy-4), radius=8, col=(255, 220, 220))

@register("combustion")
def art_combustion(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.circle((cx, cy), 44, fill=(255, 80, 20, 220))
    else:
        draw.circle((cx, cy), 20, fill=(255, 150, 30), outline=(255, 230, 100), width=2)
        for ang in range(0, 360, 40):
            rad = math.radians(ang)
            draw.line([(cx+math.cos(rad)*20, cy+math.sin(rad)*20), (cx+math.cos(rad)*48, cy+math.sin(rad)*48)], fill=(255, 70, 20), width=3)
        draw_spark_star(draw, (cx, cy), radius=18, col=(255, 255, 220))

@register("rupture")
def art_rupture(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.circle((cx, cy), 36, fill=(230, 30, 40, 200))
    else:
        # Heart shape
        pts = [(cx, cy+24), (cx-26, cy-5), (cx-14, cy-24), (cx, cy-12), (cx+14, cy-24), (cx+26, cy-5)]
        draw.polygon(pts, fill=(170, 25, 35), outline=(230, 50, 60), width=2)
        # Golden rupture cracks
        draw.line([(cx-12, cy-10), (cx+2, cy+4)], fill=(255, 215, 80), width=2)
        draw.line([(cx+2, cy+4), (cx+12, cy-2)], fill=(255, 215, 80), width=2)
        draw_spark_star(draw, (cx+2, cy+4), radius=10, col=(255, 255, 200))

@register("offering")
def art_offering(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.rectangle([cx-35, cy+8, cx+35, cy+38], fill=(220, 30, 30, 180))
    else:
        # Altar
        draw.rectangle([cx-32, cy+12, cx+32, cy+35], fill=(50, 40, 45), outline=(160, 70, 70), width=2)
        draw.polygon([(cx-15, cy+12), (cx, cy-5), (cx+15, cy+12)], fill=(230, 40, 40))
        # Sacrificial dagger poised above
        draw_dagger(draw, (cx, cy-2), (cx, cy-35), blade_w=6, guard_w=14, is_glow=False, blade_col=(180, 40, 40))
        draw_spark_star(draw, (cx, cy-2), radius=10, col=(255, 180, 180))

@register("abyssal_echo")
def art_abyssal_echo(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.circle((cx, cy), 42, fill=(120, 30, 190, 200))
    else:
        # Black hole / void vortex
        for r in [38, 28, 18]:
            draw.circle((cx, cy), r, outline=(150, 60, 220), width=2)
        draw.circle((cx, cy), 10, fill=(8, 4, 12))
        draw_spark_star(draw, (cx, cy), radius=8, col=(180, 120, 255))

@register("second_wind")
def art_second_wind(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.arc([cx-50, cy-35, cx+50, cy+35], start=-140, end=90, fill=(100, 230, 240, 180), width=16)
    else:
        draw.arc([cx-50, cy-35, cx+50, cy+35], start=-140, end=90, fill=(160, 245, 255), width=3)
        draw.arc([cx-30, cy-20, cx+30, cy+20], start=40, end=270, fill=(160, 245, 255), width=3)
        draw_spark_star(draw, (cx+25, cy), radius=12, col=(255, 255, 255))

# ----------------- BUFFS, POWERS & ENABLERS -----------------

@register("adrenaline")
def art_adrenaline(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.circle((cx, cy), 36, fill=(255, 80, 40, 220))
    else:
        # Pulsing heart
        pts = [(cx, cy+22), (cx-24, cy-4), (cx-12, cy-22), (cx, cy-10), (cx+12, cy-22), (cx+24, cy-4)]
        draw.polygon(pts, fill=(220, 30, 30), outline=(255, 120, 80), width=2)
        # Electric adrenaline surge
        draw_lightning_bolt(draw, (cx-20, cy), (cx+20, cy), is_glow=False, bolt_col=(255, 240, 120), width=3, seed=15)
        draw_spark_star(draw, (cx, cy), radius=14, col=(255, 255, 255))

@register("flex")
def art_flex(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.circle((cx, cy), 36, fill=(255, 120, 40, 180))
    else:
        # Flexing muscular arm
        draw.ellipse([cx-26, cy-12, cx+10, cy+18], fill=(160, 70, 50), outline=(220, 120, 80), width=2)
        draw.ellipse([cx-12, cy-26, cx+22, cy+4], fill=(170, 75, 55), outline=(220, 120, 80), width=2)
        # Power shock rings
        draw.arc([cx-38, cy-38, cx+38, cy+38], start=-45, end=45, fill=(255, 180, 60), width=3)
        draw_spark_star(draw, (cx+6, cy-14), radius=12, col=(255, 255, 200))

@register("battle_trance")
def art_battle_trance(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.ellipse([cx-40, cy-22, cx+40, cy+22], fill=(255, 60, 40, 200))
    else:
        # Mystic third eye
        draw.arc([cx-38, cy-20, cx+38, cy+20], start=0, end=180, fill=(255, 120, 60), width=3)
        draw.arc([cx-38, cy-20, cx+38, cy+20], start=180, end=360, fill=(255, 120, 60), width=3)
        draw.circle((cx, cy), 12, fill=(220, 30, 30), outline=(255, 230, 80), width=2)
        draw.circle((cx, cy), 4, fill=(255, 255, 255))
        draw_spark_star(draw, (cx, cy), radius=16, col=(255, 255, 220))

@register("seeing_red")
def art_seeing_red(draw, is_glow):
    c1 = (95, 64)
    c2 = (165, 64)
    if is_glow:
        draw.ellipse([c1[0]-18, c1[1]-10, c1[0]+18, c1[1]+10], fill=(255, 30, 30, 220))
        draw.ellipse([c2[0]-18, c2[1]-10, c2[0]+18, c2[1]+10], fill=(255, 30, 30, 220))
    else:
        # Glaring demonic eyes
        for c in [c1, c2]:
            draw.polygon([(c[0]-20, c[1]-2), (c[0], c[1]-8), (c[0]+20, c[1]+2), (c[0], c[1]+6)], fill=(240, 20, 20))
            draw.circle(c, 4, fill=(255, 240, 180))
            draw_spark_star(draw, c, radius=10, col=(255, 255, 200))

@register("warcry")
def art_warcry(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.arc([cx-10, cy-45, cx+60, cy+45], start=-50, end=50, fill=(255, 160, 50, 200), width=16)
    else:
        # War horn
        draw.polygon([(cx-40, cy+18), (cx-35, cy+6), (cx+15, cy-18), (cx+25, cy+18)], fill=(190, 140, 50), outline=(230, 190, 90), width=2)
        # Acoustic sonic waves
        for r in [25, 42, 58]:
            draw.arc([cx+15-r, cy-r, cx+15+r, cy+r], start=-40, end=40, fill=(255, 200, 100), width=3)
        draw_spark_star(draw, (cx+20, cy), radius=12, col=(255, 255, 220))

@register("spot_weakness")
def art_spot_weakness(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.circle((cx, cy), 32, fill=(255, 40, 40, 180))
    else:
        # Targeting optic
        draw.circle((cx, cy), 28, outline=(215, 180, 60), width=2)
        draw.line([(cx-36, cy), (cx+36, cy)], fill=(215, 180, 60), width=1)
        draw.line([(cx, cy-36), (cx, cy+36)], fill=(215, 180, 60), width=1)
        # Red vulnerability spot
        draw.circle((cx, cy), 8, fill=(240, 30, 30))
        draw_spark_star(draw, (cx, cy), radius=10, col=(255, 255, 255))

@register("limit_break")
def art_limit_break(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.circle((cx, cy), 42, fill=(255, 215, 60, 220))
    else:
        # Shattering iron chains
        draw.line([(cx-45, cy-18), (cx-15, cy-6)], fill=(160, 165, 175), width=5)
        draw.line([(cx+15, cy+6), (cx+45, cy+18)], fill=(160, 165, 175), width=5)
        # Broken link shards
        for ox, oy in [(-8, -12), (10, -10), (-6, 12), (8, 14)]:
            draw.rectangle([cx+ox-3, cy+oy-3, cx+ox+3, cy+oy+3], fill=(220, 225, 235))
        draw_spark_star(draw, (cx, cy), radius=24, col=(255, 255, 255))

@register("demon_form")
def art_demon_form(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.circle((cx, cy+6), 38, fill=(255, 40, 20, 220))
    else:
        # Demon horns
        draw.polygon([(cx-16, cy-6), (cx-38, cy-34), (cx-8, cy-18)], fill=(160, 30, 30))
        draw.polygon([(cx+16, cy-6), (cx+38, cy-34), (cx+8, cy-18)], fill=(160, 30, 30))
        draw_skull_shape(draw, cx, cy+10, r=18, is_glow=False, skull_col=(180, 30, 30), eye_col=(255, 220, 40))
        draw_spark_star(draw, (cx-8, cy+8), radius=6, col=(255, 255, 200))
        draw_spark_star(draw, (cx+8, cy+8), radius=6, col=(255, 255, 200))

@register("echo_form")
def art_echo_form(draw, is_glow):
    c1 = (105, 64)
    c2 = (155, 64)
    if is_glow:
        draw.circle(c1, 30, fill=(70, 180, 255, 180))
        draw.circle(c2, 30, fill=(70, 180, 255, 180))
    else:
        # Dual mirror silhouettes
        draw.circle(c1, 14, fill=(40, 90, 140), outline=(100, 210, 255), width=2)
        draw.circle(c2, 14, fill=(20, 60, 100), outline=(140, 230, 255), width=2)
        draw.arc([c1[0]-24, c1[1]-24, c1[0]+24, c1[1]+24], start=-60, end=60, fill=(160, 230, 255), width=2)
        draw.arc([c2[0]-24, c2[1]-24, c2[0]+24, c2[1]+24], start=-60, end=60, fill=(160, 230, 255), width=2)
        draw_spark_star(draw, c2, radius=12, col=(255, 255, 255))

@register("dark_shackles")
def art_dark_shackles(draw, is_glow):
    cx, cy = CENTER
    if is_glow:
        draw.rectangle([cx-42, cy-18, cx+42, cy+18], fill=(150, 40, 210, 180))
    else:
        # Iron manacles
        for ox in [-25, 25]:
            draw.circle((cx+ox, cy), 14, outline=(140, 145, 155), width=4)
            draw.circle((cx+ox, cy), 6, fill=(18, 14, 25))
        # Chain links
        draw.line([(cx-11, cy), (cx+11, cy)], fill=(170, 175, 185), width=4)
        draw_spark_star(draw, (cx, cy), radius=10, col=(200, 140, 255))

# ==============================================================================
# Theme Color Palettes (Card Backgrounds)
# ==============================================================================

def get_bg_for_card(card_id):
    # Distinct tailored backgrounds matching card elements
    holy_cards = {"smite", "consecration", "holy_shield", "divine_favor", "radiant_vow", "judgment", "heavens_fury", "apotheosis"}
    electric_cards = {"zap", "ball_lightning", "chain_lightning", "thunder_strike", "superconductor", "static_discharge"}
    frost_cards = {"blizzard", "frost_barrier", "glacier"}
    poison_cards = {"deadly_poison", "bouncing_flask", "crippling_cloud", "corpse_explosion", "catalyst", "envenom", "noxious_fumes", "neutralize"}
    shadow_cards = {"shiv", "blade_dance", "finisher", "cloak_and_dagger", "backflip", "shadowstep", "footwork", "infinite_blades", "accuracy", "burst", "double_tap", "storm_of_steel", "terror", "malaise", "wraith_form"}
    necromancy_cards = {"reaper", "soul_drain", "sever_soul", "exhumation", "dark_embrace", "feel_no_pain", "corruption", "abyssal_echo", "dark_shackles", "echo_form"}
    blood_cards = {"hemokinesis", "combustion", "rupture", "offering", "blood_for_blood", "feed", "anger", "seeing_red", "adrenaline", "gouge"}
    fire_cards = {"fiend_fire", "flame_barrier", "demon_form"}

    if card_id in holy_cards:
        return make_bg((35, 30, 25), (15, 12, 18), glow_col=(255, 210, 60, 160), glow_r=100)
    elif card_id in electric_cards:
        return make_bg((18, 25, 40), (10, 12, 22), glow_col=(50, 180, 255, 170), glow_r=95)
    elif card_id in frost_cards:
        return make_bg((20, 32, 45), (12, 16, 26), glow_col=(90, 210, 255, 170), glow_r=95)
    elif card_id in poison_cards:
        return make_bg((18, 32, 22), (10, 18, 14), glow_col=(40, 230, 90, 160), glow_r=95)
    elif card_id in shadow_cards:
        return make_bg((20, 24, 30), (12, 12, 18), glow_col=(60, 210, 150, 140), glow_r=90)
    elif card_id in necromancy_cards:
        return make_bg((28, 18, 38), (14, 10, 22), glow_col=(140, 50, 220, 160), glow_r=95)
    elif card_id in blood_cards:
        return make_bg((40, 16, 20), (18, 8, 12), glow_col=(240, 30, 40, 170), glow_r=95)
    elif card_id in fire_cards:
        return make_bg((42, 20, 14), (18, 10, 8), glow_col=(255, 100, 30, 180), glow_r=95)
    else:
        # Default dark steel / combat
        return make_bg((26, 24, 32), (14, 12, 18), glow_col=(180, 160, 210, 120), glow_r=85)

# ==============================================================================
# Generator Main Loop
# ==============================================================================

def generate_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    total = len(CARD_ARTISTS)
    print(f"Generating high-resolution card artwork for {total} cards...")

    for idx, (card_id, artist_fn) in enumerate(CARD_ARTISTS.items(), 1):
        bg = get_bg_for_card(card_id)
        img = render_art(bg, artist_fn)
        out_path = os.path.join(OUTPUT_DIR, f"{card_id}.png")
        img.save(out_path, format="PNG")
        print(f"[{idx}/{total}] Generated {card_id}.png")

    print(f"\nSuccessfully generated {total} card art illustrations in {OUTPUT_DIR}!")

if __name__ == "__main__":
    generate_all()
