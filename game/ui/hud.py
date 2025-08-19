from __future__ import annotations
import pygame

from game.core.profiling import FrameProfiler


class HUD:
	def __init__(self, localization, config):
		self.localization = localization
		self.config = config
		self.font = pygame.font.SysFont("DejaVu Sans", 18)

	def draw(self, surface: pygame.Surface, player, enemies, projectiles, config, profiler: FrameProfiler) -> None:
		text = f"HP: {int(player.health)} | Enemies: {sum(1 for e in enemies if e.health > 0)} | Proj: {sum(1 for p in projectiles.projectiles if p.active)} | FPS: {profiler.fps:.0f}"
		render = self.font.render(text, True, (235, 235, 245))
		surface.blit(render, (8, 8))