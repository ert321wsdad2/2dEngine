from __future__ import annotations
from typing import List
import pygame


class Particle:
	__slots__ = ("active", "position", "velocity", "color", "ttl")

	def __init__(self):
		self.active = False
		self.position = pygame.Vector2(0, 0)
		self.velocity = pygame.Vector2(0, 0)
		self.color = (255, 255, 255)
		self.ttl = 0.0


class ParticleSystem:
	def __init__(self, max_particles: int = 512):
		self.particles: List[Particle] = [Particle() for _ in range(max_particles)]

	def spawn(self, pos, vel, color, ttl: float) -> None:
		for p in self.particles:
			if not p.active:
				p.active = True
				p.position.update(pos[0], pos[1])
				p.velocity.update(vel[0], vel[1])
				p.color = color
				p.ttl = ttl
				return

	def update(self) -> None:
		dt = 1.0 / 60.0
		for p in self.particles:
			if not p.active:
				continue
			p.ttl -= dt
			if p.ttl <= 0:
				p.active = False
				continue
			p.position += p.velocity * dt

	def draw(self, surface: pygame.Surface, camera) -> None:
		for p in self.particles:
			if not p.active:
				continue
			sx, sy = camera.world_to_screen(p.position.xy)
			surface.fill(p.color, rect=pygame.Rect(int(sx), int(sy), 2, 2))