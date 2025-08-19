from __future__ import annotations
import pygame


class PauseMenu:
	def __init__(self, localization, config, input_manager):
		self.localization = localization
		self.config = config
		self.input = input_manager
		self.is_open = False
		self.request_quit = False
		self.font = pygame.font.SysFont("DejaVu Sans", 28)
		self._selected = 0
		self._options = ["resume", "quit"]

	def toggle(self) -> None:
		self.is_open = not self.is_open

	def process_event(self, event: pygame.event.Event) -> None:
		pass

	def update(self) -> None:
		keys = pygame.key.get_pressed()
		if keys[pygame.K_ESCAPE]:
			self.is_open = False
			return
		if keys[pygame.K_UP] or keys[pygame.K_w]:
			self._selected = (self._selected - 1) % len(self._options)
		if keys[pygame.K_DOWN] or keys[pygame.K_s]:
			self._selected = (self._selected + 1) % len(self._options)
		if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
			if self._options[self._selected] == "resume":
				self.is_open = False
			elif self._options[self._selected] == "quit":
				self.request_quit = True

	def draw(self, surface: pygame.Surface) -> None:
		w, h = surface.get_size()
		overlay = pygame.Surface((w, h), pygame.SRCALPHA)
		overlay.fill((10, 10, 10, 160))
		surface.blit(overlay, (0, 0))

		title = self.font.render("PAUSED", True, (240, 240, 250))
		rect = title.get_rect(center=(w // 2, h // 2 - 80))
		surface.blit(title, rect)
		for i, opt in enumerate(self._options):
			label = self.font.render(opt.upper(), True, (255, 240, 200) if i == self._selected else (200, 200, 200))
			lr = label.get_rect(center=(w // 2, h // 2 + i * 36))
			surface.blit(label, lr)