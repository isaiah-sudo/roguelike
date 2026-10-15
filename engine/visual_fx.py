"""
Visual effects: screen shake, Bezier curve targeting arrows, and glow utilities.
"""
import pygame
import math
import random

class ScreenShake:
    def __init__(self):
        self.duration = 0.0
        self.intensity = 0.0
        self.offset_x = 0
        self.offset_y = 0

    def start(self, intensity=6.0, duration=0.25):
        self.intensity = max(self.intensity, intensity)
        self.duration = max(self.duration, duration)

    def update(self, dt):
        if self.duration > 0:
            self.duration -= dt
            decay = max(0.0, self.duration)
            self.offset_x = random.uniform(-self.intensity, self.intensity) * (decay / 0.25)
            self.offset_y = random.uniform(-self.intensity, self.intensity) * (decay / 0.25)
        else:
            self.offset_x = 0
            self.offset_y = 0
            self.intensity = 0.0

def draw_targeting_arrow(surface, start_pos, end_pos, color=(255, 70, 70)):
    """
    Draw a curved quadratic Bezier trajectory arrow from card to target.
    """
    x1, y1 = start_pos
    x2, y2 = end_pos

    # Control point bowed upward
    cx = (x1 + x2) / 2
    cy = min(y1, y2) - max(60, abs(x2 - x1) * 0.2)

    points = []
    num_points = 24
    for i in range(num_points + 1):
        t = i / num_points
        # Quadratic bezier formula: (1-t)^2 * P0 + 2(1-t)t * P1 + t^2 * P2
        px = (1 - t)**2 * x1 + 2 * (1 - t) * t * cx + t**2 * x2
        py = (1 - t)**2 * y1 + 2 * (1 - t) * t * cy + t**2 * y2
        points.append((px, py))

    # Draw graduated dotted / glowing segments
    for i in range(len(points) - 1):
        t = i / num_points
        radius = int(2 + 4 * t)
        alpha = int(120 + 135 * t)
        dot_surf = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(dot_surf, (*color, alpha), (radius + 1, radius + 1), radius)
        surface.blit(dot_surf, (int(points[i][0] - radius - 1), int(points[i][1] - radius - 1)))

    # Draw arrowhead at end_pos
    # Calculate tangent angle at t=1
    dx = 2 * (1 - 1.0) * (cx - x1) + 2 * 1.0 * (x2 - cx)
    dy = 2 * (1 - 1.0) * (cy - y1) + 2 * 1.0 * (y2 - cy)
    angle = math.atan2(dy, dx)

    arrow_size = 18
    p1 = (x2, y2)
    p2 = (x2 - arrow_size * math.cos(angle - math.pi / 6), y2 - arrow_size * math.sin(angle - math.pi / 6))
    p3 = (x2 - arrow_size * math.cos(angle + math.pi / 6), y2 - arrow_size * math.sin(angle + math.pi / 6))

    pygame.draw.polygon(surface, color, [p1, p2, p3])
    pygame.draw.polygon(surface, (255, 255, 255), [p1, p2, p3], 2)
