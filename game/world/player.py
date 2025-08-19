from __future__ import annotations
import pygame
from typing import List, Tuple

from game.core.input import InputManager
from .projectiles import ProjectilePool
from .particles import ParticleSystem
from .tilemap import TileMap


class Player:
	def __init__(self, spawn_pos: Tuple[float, float], input_manager: InputManager, projectiles: ProjectilePool, particles: ParticleSystem, tile_map: TileMap):
		self.position = pygame.Vector2(spawn_pos)
		self.velocity = pygame.Vector2(0, 0)
		self.size = pygame.Vector2(24, 28)
		self.input = input_manager
		self.projectiles = projectiles
		self.particles = particles
		self.tile_map = tile_map
		self.move_accel = 1800.0
		self.move_decel = 2400.0
		self.max_speed = 220.0
		self.fire_cooldown = 0.2
		self._fire_timer = 0.0
		self.health = 100.0
		self.armor = 0.1
		self.is_dead = False
		self.statuses: List[Tuple[str, float]] = []

	@property
	def rect(self) -> pygame.Rect:
		return pygame.Rect(int(self.position.x - self.size.x * 0.5), int(self.position.y - self.size.y * 0.5), int(self.size.x), int(self.size.y))

	def update(self, camera) -> None:
		dt = 1.0 / 60.0
		if self.is_dead:
			return
		move_x, move_y = self.input.get_move_vector()
		input_dir = pygame.Vector2(move_x, move_y)
		if input_dir.length_squared() > 1e-5:
			input_dir = input_dir.normalize()
			desired = input_dir * self.max_speed
			self.velocity = self._approach(self.velocity, desired, self.move_accel * dt)
		else:
			self.velocity = self._approach(self.velocity, pygame.Vector2(0, 0), self.move_decel * dt)

		dx = self.velocity.x * dt
		dy = self.velocity.y * dt
		_, _, new_rect = self.tile_map.resolve_movement(self.rect, dx, dy)
		self.position.update(new_rect.centerx, new_rect.centery)

		dps = self.tile_map.get_damage_in_rect_per_second(new_rect)
		if dps > 0.0:
			self.take_damage(dps * dt, damage_type="environment")

		self._fire_timer -= dt
		if self.input.is_action_held("fire") and self._fire_timer <= 0.0:
			mouse_world = camera.screen_to_world(self.input.get_mouse_screen())
			direction = pygame.Vector2(mouse_world[0] - self.position.x, mouse_world[1] - self.position.y)
			if direction.length_squared() > 1e-6:
				direction = direction.normalize()
				self.projectiles.spawn(self.position.xy, direction.xy, speed=520.0, ttl=1.2, damage=15.0, owner="player", spread_deg=4.0, knockback=140.0)
				self._fire_timer = self.fire_cooldown

	def draw(self, surface: pygame.Surface, camera) -> None:
		sx, sy = camera.world_to_screen(self.position.xy)
		rect = pygame.Rect(0, 0, int(self.size.x), int(self.size.y))
		rect.center = (sx, sy)
		color = (80, 200, 120) if not self.is_dead else (80, 80, 80)
		pygame.draw.rect(surface, color, rect, border_radius=4)

	def take_damage(self, amount: float, damage_type: str = "") -> None:
		if self.is_dead:
			return
		effective = max(0.0, amount * (1.0 - self.armor))
		self.health -= effective
		if self.health <= 0.0:
			self.is_dead = True

	def _approach(self, current: pygame.Vector2, target: pygame.Vector2, delta: float) -> pygame.Vector2:
		diff = target - current
		length = diff.length()
		if length <= delta or length < 1e-6:
			return target
		return current + diff.normalize() * delta