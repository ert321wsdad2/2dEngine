import pygame
from typing import Optional

from .core import Scene
from .camera import Camera


class Game:
    """Minimal 2D engine loop on top of pygame with a single active scene."""

    def __init__(self, width: int = 960, height: int = 540, title: str = "Pygame 2D Engine", target_fps: int = 60, background_color: tuple[int, int, int] = (20, 22, 26)) -> None:
        pygame.init()
        self.width = width
        self.height = height
        self.background_color = background_color
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.target_fps = target_fps
        self.scene: Scene = Scene()
        self.scene.camera = Camera(width, height)
        self._running = False
        self._show_debug = False

    def set_scene(self, scene: Scene) -> None:
        self.scene = scene
        if self.scene.camera is None:
            self.scene.camera = Camera(self.width, self.height)

    def stop(self) -> None:
        self._running = False

    def run(self) -> None:
        self._running = True
        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
                    self._show_debug = not self._show_debug
                else:
                    self.scene.handle_event(event)

            dt = self.clock.tick(self.target_fps) / 1000.0

            self.scene.update(dt)

            self.screen.fill(self.background_color)
            self.scene.draw(self.screen)

            if self._show_debug:
                self._draw_debug_overlay(dt)

            pygame.display.flip()

        pygame.quit()

    def _draw_debug_overlay(self, dt: float) -> None:
        fps = self.clock.get_fps()
        ms = (dt * 1000.0)
        num_objects = len(self.scene.game_objects)
        camera: Optional[Camera] = self.scene.camera  # type: ignore
        cam_pos = (0.0, 0.0)
        target_pos = None
        if camera is not None:
            cam_pos = (camera.position.x, camera.position.y)
            if getattr(camera, "_target", None) is not None:
                t = camera._target
                target_pos = (getattr(t, "position").x, getattr(t, "position").y)  # type: ignore
        lines = [
            f"FPS: {fps:5.1f}",
            f"Frame: {ms:6.2f} ms",
            f"Objects: {num_objects}",
            f"Camera: {cam_pos[0]:.1f}, {cam_pos[1]:.1f}",
        ]
        if target_pos is not None:
            lines.append(f"Target: {target_pos[0]:.1f}, {target_pos[1]:.1f}")
        mouse = pygame.mouse.get_pos()
        if camera is not None:
            wx, wy = camera.screen_to_world(mouse)
            lines.append(f"Mouse: {mouse[0]}, {mouse[1]}  World: {wx:.1f}, {wy:.1f}")
        font = pygame.font.SysFont("consolas", 16)
        y = 8
        bg = (0, 0, 0, 160)
        for text in lines:
            surf = font.render(text, True, (230, 230, 230))
            rect = surf.get_rect(topleft=(8, y))
            pad = 4
            box = pygame.Surface((rect.width + pad * 2, rect.height + pad * 2), pygame.SRCALPHA)
            box.fill(bg)
            self.screen.blit(box, (rect.left - pad, rect.top - pad))
            self.screen.blit(surf, rect)
            y += rect.height + 6