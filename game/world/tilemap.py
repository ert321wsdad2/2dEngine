from __future__ import annotations
import pygame
import random
from typing import Dict, List, Tuple


class TileMap:
	def __init__(self, tiles_w: int, tiles_h: int, tile_size: int):
		self.tiles_w = tiles_w
		self.tiles_h = tiles_h
		self.tile_size = tile_size
		self.pixel_width = tiles_w * tile_size
		self.pixel_height = tiles_h * tile_size

		self.ground: List[List[int]] = [[0 for _ in range(tiles_w)] for _ in range(tiles_h)]
		self.collision: List[List[bool]] = [[False for _ in range(tiles_w)] for _ in range(tiles_h)]
		self.zones: List[Dict] = []

		self._rng = random.Random(1337)
		self._generate()

		self._chunk_size_tiles = 32
		self._chunk_cache: Dict[Tuple[int, int], Tuple[pygame.Surface, pygame.Rect]] = {}

	def _generate(self) -> None:
		for x in range(self.tiles_w):
			self.collision[0][x] = True
			self.collision[self.tiles_h - 1][x] = True
		for y in range(self.tiles_h):
			self.collision[y][0] = True
			self.collision[y][self.tiles_w - 1] = True
		for _ in range(int(self.tiles_w * self.tiles_h * 0.07)):
			x = self._rng.randint(2, self.tiles_w - 3)
			y = self._rng.randint(2, self.tiles_h - 3)
			w = self._rng.randint(1, 3)
			h = self._rng.randint(1, 3)
			for yy in range(y, min(y + h, self.tiles_h - 1)):
				for xx in range(x, min(x + w, self.tiles_w - 1)):
					self.collision[yy][xx] = True
		dz = pygame.Rect(10 * self.tile_size, 10 * self.tile_size, 3 * self.tile_size, 3 * self.tile_size)
		self.zones.append({"type": "damage", "rect": dz, "dps": 10})

	def draw(self, surface: pygame.Surface, camera) -> None:
		view_rect = pygame.Rect(0, 0, camera.view_width, camera.view_height)
		view_rect.center = (int(camera.position_x), int(camera.position_y))

		min_tx = max(0, int((view_rect.left - 1) // self.tile_size))
		max_tx = min(self.tiles_w - 1, int((view_rect.right + 1) // self.tile_size))
		min_ty = max(0, int((view_rect.top - 1) // self.tile_size))
		max_ty = min(self.tiles_h - 1, int((view_rect.bottom + 1) // self.tile_size))

		chunk = self._chunk_size_tiles
		start_cx = min_tx // chunk
		end_cx = max_tx // chunk
		start_cy = min_ty // chunk
		end_cy = max_ty // chunk

		for cy in range(start_cy, end_cy + 1):
			for cx in range(start_cx, end_cx + 1):
				key = (cx, cy)
				if key not in self._chunk_cache:
					self._build_chunk_surface(cx, cy)
				chunk_surface, chunk_rect = self._chunk_cache[key]
				screen_pos = camera.world_to_screen((chunk_rect.x + chunk_rect.w * 0.5, chunk_rect.y + chunk_rect.h * 0.5))
				draw_rect = chunk_surface.get_rect()
				draw_rect.center = screen_pos
				surface.blit(chunk_surface, draw_rect)

		color_wall = (48, 48, 60)
		for ty in range(min_ty, max_ty + 1):
			for tx in range(min_tx, max_tx + 1):
				if self.collision[ty][tx]:
					wx = tx * self.tile_size
					wy = ty * self.tile_size
					rect = pygame.Rect(wx, wy, self.tile_size, self.tile_size)
					sx, sy = camera.world_to_screen((rect.centerx, rect.centery))
					r = pygame.Rect(0, 0, rect.w, rect.h)
					r.center = (sx, sy)
					pygame.draw.rect(surface, color_wall, r)

		for zone in self.zones:
			zr = zone["rect"]
			if view_rect.colliderect(zr):
				sx, sy = camera.world_to_screen((zr.centerx, zr.centery))
				rr = pygame.Rect(0, 0, zr.w, zr.h)
				rr.center = (sx, sy)
				pygame.draw.rect(surface, (180, 50, 50), rr, width=2)

	def _build_chunk_surface(self, cx: int, cy: int) -> None:
		chunk = self._chunk_size_tiles
		x0 = cx * chunk
		y0 = cy * chunk
		x1 = min(self.tiles_w, x0 + chunk)
		y1 = min(self.tiles_h, y0 + chunk)
		surf = pygame.Surface(((x1 - x0) * self.tile_size, (y1 - y0) * self.tile_size)).convert()
		surf.fill((24, 24, 28))
		color_a = (30, 30, 36)
		color_b = (34, 34, 40)
		for ty in range(y0, y1):
			for tx in range(x0, x1):
				color = color_a if (tx + ty) % 2 == 0 else color_b
				pygame.draw.rect(surf, color, pygame.Rect((tx - x0) * self.tile_size, (ty - y0) * self.tile_size, self.tile_size, self.tile_size))
		rect = pygame.Rect(x0 * self.tile_size, y0 * self.tile_size, surf.get_width(), surf.get_height())
		self._chunk_cache[(cx, cy)] = (surf, rect)

	def collides_aabb(self, rect: pygame.Rect) -> bool:
		min_tx = max(0, rect.left // self.tile_size)
		max_tx = min(self.tiles_w - 1, (rect.right - 1) // self.tile_size)
		min_ty = max(0, rect.top // self.tile_size)
		max_ty = min(self.tiles_h - 1, (rect.bottom - 1) // self.tile_size)
		for ty in range(min_ty, max_ty + 1):
			for tx in range(min_tx, max_tx + 1):
				if self.collision[ty][tx]:
					return True
		return False

	def resolve_movement(self, rect: pygame.Rect, dx: float, dy: float):
		new_rect = rect.copy()
		new_rect.x += int(dx)
		if self.collides_aabb(new_rect):
			step = 1 if dx > 0 else -1
			while int(dx) != 0:
				new_rect.x -= step
				dx -= step
				if not self.collides_aabb(new_rect):
					break
			else:
				new_rect.x += step
				dx = 0
		new_rect.y += int(dy)
		if self.collides_aabb(new_rect):
			step = 1 if dy > 0 else -1
			while int(dy) != 0:
				new_rect.y -= step
				dy -= step
				if not self.collides_aabb(new_rect):
					break
			else:
				new_rect.y += step
				dy = 0
		new_rect.clamp_ip(pygame.Rect(0, 0, self.pixel_width, self.pixel_height))
		return dx, dy, new_rect

	def raycast_block(self, start: Tuple[float, float], end: Tuple[float, float]) -> bool:
		x0, y0 = start
		x1, y1 = end
		dx = x1 - x0
		dy = y1 - y0
		steps = int(max(abs(dx), abs(dy)) // self.tile_size) + 1
		for i in range(steps + 1):
			t = i / steps
			x = x0 + dx * t
			y = y0 + dy * t
			tx = int(x) // self.tile_size
			ty = int(y) // self.tile_size
			if tx < 0 or ty < 0 or tx >= self.tiles_w or ty >= self.tiles_h:
				continue
			if self.collision[ty][tx]:
				return True
		return False

	def get_damage_in_rect_per_second(self, rect: pygame.Rect) -> float:
		total = 0.0
		for zone in self.zones:
			if zone.get("type") == "damage" and rect.colliderect(zone["rect"]):
				total += float(zone.get("dps", 0.0))
		return total