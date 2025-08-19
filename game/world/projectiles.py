from __future__ import annotations
import math
import random
from typing import List, Tuple
import pygame

from .tilemap import TileMap


class Projectile:
	__slots__ = ("active", "position", "velocity", "ttl", "damage", "owner", "knockback")

	def __init__(self):
		self.active = False
		self.position = pygame.Vector2(0, 0)
		self.velocity = pygame.Vector2(0, 0)
		self.ttl = 0.0
		self.damage = 0.0
		self.owner = "player"
		self.knockback = 0.0


class ProjectilePool:
	def __init__(self, max_projectiles: int = 256):
		self.projectiles: List[Projectile] = [Projectile() for _ in range(max_projectiles)]

	def spawn(self, position: Tuple[float, float], direction: Tuple[float, float], speed: float, ttl: float, damage: float, owner: str, spread_deg: float = 0.0, knockback: float = 0.0) -> None:
		for p in self.projectiles:
			if not p.active:
				angle = math.atan2(direction[1], direction[0])
				if spread_deg > 0.0:
					spread = math.radians(random.uniform(-spread_deg * 0.5, spread_deg * 0.5))
					angle += spread
				p.active = True
				p.position.update(position[0], position[1])
				p.velocity.update(math.cos(angle) * speed, math.sin(angle) * speed)
				p.ttl = ttl
				p.damage = damage
				p.owner = owner
				p.knockback = knockback
				return

	def update(self, tile_map: TileMap, player, enemies: List[object]):
		dt = 1.0 / 60.0
		for p in self.projectiles:
			if not p.active:
				continue
			p.ttl -= dt
			if p.ttl <= 0:
				p.active = False
				continue
			# Move
			dx = p.velocity.x * dt
			dy = p.velocity.y * dt
			rect = pygame.Rect(int(p.position.x) - 3, int(p.position.y) - 3, 6, 6)
			dx, dy, new_rect = tile_map.resolve_movement(rect, dx, dy)
			p.position.update(new_rect.centerx, new_rect.centery)

			# Collision with walls
			if abs(dx) < 1e-5 and abs(dy) < 1e-5 and tile_map.collides_aabb(new_rect):
				p.active = False
				continue

			# Hits
			if p.owner == "player":
				for e in enemies:
					if new_rect.colliderect(e.rect):
						e.take_damage(p.damage)
						p.active = False
						break
			elif p.owner == "enemy":
				if new_rect.colliderect(player.rect):
					player.take_damage(p.damage, damage_type="projectile")
					p.active = False

	def draw(self, surface: pygame.Surface, camera) -> None:
		for p in self.projectiles:
			if not p.active:
				continue
			sx, sy = camera.world_to_screen(p.position.xy)
			pygame.draw.circle(surface, (230, 230, 80) if p.owner == "player" else (230, 100, 100), (int(sx), int(sy)), 3)