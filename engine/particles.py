"""
Particle effects system for spells, slashes, blocks, and ambient dungeon fog.
"""
import pygame
import random
import math

class Particle:
    def __init__(self, x, y, vx, vy, color, radius, lifetime, shape="circle", gravity=0.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.radius = radius
        self.initial_radius = radius
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.shape = shape
        self.gravity = gravity

    def update(self, dt):
        self.lifetime -= dt
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.vy += self.gravity * dt * 60
        # Shrink particle as it expires
        progress = max(0.0, self.lifetime / self.max_lifetime)
        self.radius = self.initial_radius * progress

    def draw(self, surface):
        if self.radius <= 0.5:
            return
        alpha = int(255 * (self.lifetime / self.max_lifetime))
        color = (*self.color[:3], max(0, min(255, alpha)))
        
        particle_surf = pygame.Surface((int(self.radius * 2) + 2, int(self.radius * 2) + 2), pygame.SRCALPHA)
        center = (int(self.radius) + 1, int(self.radius) + 1)
        
        if self.shape == "circle":
            pygame.draw.circle(particle_surf, color, center, int(self.radius))
        elif self.shape == "spark":
            points = [
                (center[0], center[1] - self.radius),
                (center[0] + self.radius, center[1]),
                (center[0], center[1] + self.radius),
                (center[0] - self.radius, center[1])
            ]
            pygame.draw.polygon(particle_surf, color, points)
        
        surface.blit(particle_surf, (int(self.x - center[0]), int(self.y - center[1])))

class DamagePopup:
    def __init__(self, x, y, text, color, is_crit=False):
        self.x = x + random.uniform(-15, 15)
        self.y = y
        self.text = str(text)
        self.color = color
        self.is_crit = is_crit
        self.lifetime = 1.0
        self.max_lifetime = 1.0
        self.vy = -1.8 if not is_crit else -2.5

    def update(self, dt):
        self.lifetime -= dt
        self.y += self.vy * dt * 60
        self.vy += 0.05 * dt * 60  # decelerate upward movement

    def draw(self, surface, font):
        if self.lifetime <= 0:
            return
        alpha = int(255 * min(1.0, self.lifetime / 0.3))
        text_surf = font.render(self.text, True, self.color)
        if alpha < 255:
            text_surf.set_alpha(alpha)
        
        # Shadow
        shadow_surf = font.render(self.text, True, (10, 10, 15))
        if alpha < 255:
            shadow_surf.set_alpha(alpha)
        surface.blit(shadow_shadow := shadow_surf, (int(self.x) + 2, int(self.y) + 2))
        surface.blit(text_surf, (int(self.x), int(self.y)))

class ParticleManager:
    def __init__(self):
        self.particles = []
        self.popups = []

    def spawn_burst(self, x, y, color, count=16, speed=4.0, radius=4, shape="circle", gravity=0.0):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(speed * 0.4, speed)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            lifetime = random.uniform(0.3, 0.7)
            self.particles.append(Particle(x, y, vx, vy, color, radius, lifetime, shape, gravity))

    def spawn_slash(self, x, y, color=(240, 70, 70)):
        for i in range(25):
            offset = (i - 12) * 4
            px = x + offset
            py = y - offset * 0.8
            vx = random.uniform(-1, 1)
            vy = random.uniform(-1, 1)
            self.particles.append(Particle(px, py, vx, vy, color, random.uniform(2, 5), 0.35, "spark"))

    def spawn_block(self, x, y):
        self.spawn_burst(x, y, (80, 170, 255), count=20, speed=3.5, radius=3.5, shape="spark")

    def spawn_poison(self, x, y):
        for _ in range(15):
            vx = random.uniform(-1.0, 1.0)
            vy = random.uniform(-2.5, -0.5)
            self.particles.append(Particle(x + random.uniform(-20, 20), y, vx, vy, (80, 230, 80), random.uniform(3, 6), 0.6, "circle", gravity=-0.02))

    def spawn_popup(self, x, y, text, color, is_crit=False):
        self.popups.append(DamagePopup(x, y, text, color, is_crit))

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.lifetime > 0]

        for pop in self.popups:
            pop.update(dt)
        self.popups = [pop for pop in self.popups if pop.lifetime > 0]

    def draw(self, surface, font):
        for p in self.particles:
            p.draw(surface)
        for pop in self.popups:
            pop.draw(surface, font)
