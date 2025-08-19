from __future__ import annotations
import pygame
import random
from typing import Callable, Tuple

from .tilemap import TileMap
from .projectiles import ProjectilePool
from .particles import ParticleSystem


class Enemy:
	def __init__(self, spawn_pos: Tuple[float, float], tile_map: TileMap, target_getter: Callable[[], object], projectiles: ProjectilePool, particles: ParticleSystem):
		self.position = pygame.Vector2(spawn_pos)
		self.velocity = pygame.Vector2(0, 0)
		self.size = pygame.Vector2(24, 24)
		self.tile_map = tile_map
		self.get_target = target_getter
		self.projectiles = projectiles
		self.particles = particles
		self.state = "patrol"
		self.health = 50.0
		self._rng = random.Random(42)
		self._timer = 0.0
		self._fire_timer = 0.0
		self.patrol_dir = pygame.Vector2(1, 0)
		self.max_speed = 160.0

	@property
	def rect(self) -> pygame.Rect:
		return pygame.Rect(int(self.position.x - self.size.x * 0.5), int(self.position.y - self.size.y * 0.5), int(self.size.x), int(self.size.y))

	def update(self) -> None:
		dt = 1.0 / 60.0
		self._timer += dt
		self._fire_timer -= dt
		target = self.get_target()
		target_pos = pygame.Vector2(target.position.x, target.position.y)

		dist = (target_pos - self.position).length()
		los = not self.tile_map.raycast_block(self.position.xy, target_pos.xy)

		if self.state == "patrol":
			if dist < 280 and los:
				self.state = "chase"
			else:
				if self._timer > 2.0:
					self._timer = 0.0
					angle = self._rng.uniform(0, 6.283)
					self.patrol_dir = pygame.Vector2(pygame.math.Vector2(1, 0).rotate_rad(angle))
				self._move(self.patrol_dir, dt)
		elif self.state == "chase":
			if dist > 420 or not los:
				self.state = "patrol"
			else:
				direction = (target_pos - self.position)
				if direction.length_squared() > 1e-6:
					direction = direction.normalize()
				self._move(direction, dt)
				if dist < 260 and self._fire_timer <= 0.0:
					self.projectiles.spawn(self.position.xy, (target_pos - self.position).normalize().xy, speed=400.0, ttl=1.5, damage=8.0, owner="enemy", spread_deg=6.0, knockback=80.0)
					self._fire_timer = 0.9

	def _move(self, direction: pygame.Vector2, dt: float) -> None:
		desired = direction * self.max_speed
		self.velocity = self._approach(self.velocity, desired, 1600 * dt)
		dx = self.velocity.x * dt
		dy = self.velocity.y * dt
		_, _, new_rect = self.tile_map.resolve_movement(self.rect, dx, dy)
		self.position.update(new_rect.centerx, new_rect.centery)

	def draw(self, surface: pygame.Surface, camera) -> None:
		sx, sy = camera.world_to_screen(self.position.xy)
		rect = pygame.Rect(0, 0, int(self.size.x), int(self.size.y))
		rect.center = (sx, sy)
		pygame.draw.rect(surface, (200, 80, 80), rect, border_radius=4)

	def take_damage(self, amount: float) -> None:
		self.health -= amount
		if self.health <= 0.0:
			# simple death effect placeholder
			self.position.xy = (-1000, -1000)

	def _approach(self, current: pygame.Vector2, target: pygame.Vector2, delta: float) -> pygame.Vector2:
		diff = target - current
		length = diff.length()
		if length <= delta or length < 1e-6:
			return target
		return current + diff.normalize() * delta