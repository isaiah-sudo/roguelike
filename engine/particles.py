"""
Particle effects system for spells, slashes, blocks, shockwaves, and ambient dungeon fog.
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

class ShockwaveRing:
    def __init__(self, x, y, color=(255, 120, 80), max_radius=42, lifetime=0.3):
        self.x = x
        self.y = y
        self.color = color
        self.max_radius = max_radius
        self.lifetime = lifetime
        self.max_lifetime = lifetime

    def update(self, dt):
        self.lifetime -= dt

    def draw(self, surface):
        if self.lifetime <= 0:
            return
        progress = 1.0 - (self.lifetime / self.max_lifetime)
        cur_radius = int(8 + (self.max_radius - 8) * progress)
        alpha = int(230 * (1.0 - progress))
        if cur_radius <= 0 or alpha <= 0:
            return
        ring_surf = pygame.Surface((cur_radius * 2 + 4, cur_radius * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (*self.color[:3], alpha), (cur_radius + 2, cur_radius + 2), cur_radius, width=2)
        surface.blit(ring_surf, (self.x - cur_radius - 2, self.y - cur_radius - 2))

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
        surface.blit(shadow_surf, (int(self.x) + 2, int(self.y) + 2))
        surface.blit(text_surf, (int(self.x), int(self.y)))

class ParticleManager:
    def __init__(self):
        self.particles = []
        self.shockwaves = []
        self.popups = []

    def spawn_burst(self, x, y, color, count=16, speed=4.0, radius=4, shape="circle", gravity=0.0):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            spd = random.uniform(speed * 0.4, speed)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            lifetime = random.uniform(0.3, 0.7)
            self.particles.append(Particle(x, y, vx, vy, color, radius, lifetime, shape, gravity))

    def spawn_shockwave(self, x, y, color=(255, 140, 80), max_radius=45, duration=0.3):
        self.shockwaves.append(ShockwaveRing(x, y, color, max_radius, duration))

    def spawn_slash(self, x, y, color=(240, 70, 70)):
        self.spawn_shockwave(x, y, color=color, max_radius=38, duration=0.25)
        for i in range(25):
            offset = (i - 12) * 4
            px = x + offset
            py = y - offset * 0.8
            vx = random.uniform(-1, 1)
            vy = random.uniform(-1, 1)
            self.particles.append(Particle(px, py, vx, vy, color, random.uniform(2, 5), 0.35, "spark"))

    def spawn_block(self, x, y):
        self.spawn_shockwave(x, y, color=(100, 200, 255), max_radius=36, duration=0.25)
        self.spawn_burst(x, y, (80, 170, 255), count=20, speed=3.5, radius=3.5, shape="spark")

    def spawn_poison(self, x, y):
        for _ in range(15):
            vx = random.uniform(-1.0, 1.0)
            vy = random.uniform(-2.5, -0.5)
            self.particles.append(Particle(x + random.uniform(-20, 20), y, vx, vy, (80, 230, 80), random.uniform(3, 6), 0.6, "circle", gravity=-0.02))

    def spawn_popup(self, x, y, text, color, is_crit=False):
        if is_crit:
            self.spawn_shockwave(x, y, color=(255, 230, 100), max_radius=52, duration=0.35)
        self.popups.append(DamagePopup(x, y, text, color, is_crit))

    def update(self, dt):
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.lifetime > 0]

        for s in self.shockwaves:
            s.update(dt)
        self.shockwaves = [s for s in self.shockwaves if s.lifetime > 0]

        for pop in self.popups:
            pop.update(dt)
        self.popups = [pop for pop in self.popups if pop.lifetime > 0]

    def draw(self, surface, font):
        for s in self.shockwaves:
            s.draw(surface)
        for p in self.particles:
            p.draw(surface)
        for pop in self.popups:
            pop.draw(surface, font)
