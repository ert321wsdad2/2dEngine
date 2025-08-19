from __future__ import annotations
from typing import Tuple


class Camera:
	def __init__(self, view_width: int, view_height: int, world_width: int, world_height: int):
		self.view_width = view_width
		self.view_height = view_height
		self.world_width = world_width
		self.world_height = world_height
		self.position_x = 0.0
		self.position_y = 0.0
		self.deadzone_width = view_width * 0.35
		self.deadzone_height = view_height * 0.35
		self.zoom = 1.0
		self.shake_timer = 0.0
		self.shake_magnitude = 0.0

	def resize_view(self, w: int, h: int) -> None:
		self.view_width = w
		self.view_height = h
		self.deadzone_width = w * 0.35
		self.deadzone_height = h * 0.35
		self.clamp_to_world()

	def update_follow(self, target_world_pos: Tuple[float, float]) -> None:
		tx, ty = target_world_pos
		left = self.position_x - self.deadzone_width * 0.5
		right = self.position_x + self.deadzone_width * 0.5
		top = self.position_y - self.deadzone_height * 0.5
		bottom = self.position_y + self.deadzone_height * 0.5
		if tx < left:
			self.position_x = tx + self.deadzone_width * 0.5
		elif tx > right:
			self.position_x = tx - self.deadzone_width * 0.5
		if ty < top:
			self.position_y = ty + self.deadzone_height * 0.5
		elif ty > bottom:
			self.position_y = ty - self.deadzone_height * 0.5
		self.clamp_to_world()

	def clamp_to_world(self) -> None:
		half_w = self.view_width * 0.5
		half_h = self.view_height * 0.5
		self.position_x = max(half_w, min(self.world_width - half_w, self.position_x))
		self.position_y = max(half_h, min(self.world_height - half_h, self.position_y))

	def world_to_screen(self, world_pos: Tuple[float, float]) -> Tuple[int, int]:
		wx, wy = world_pos
		sx = int(wx - self.position_x + self.view_width * 0.5)
		sy = int(wy - self.position_y + self.view_height * 0.5)
		return sx, sy

	def screen_to_world(self, screen_pos: Tuple[int, int]) -> Tuple[float, float]:
		sx, sy = screen_pos
		wx = sx + self.position_x - self.view_width * 0.5
		wy = sy + self.position_y - self.view_height * 0.5
		return wx, wy