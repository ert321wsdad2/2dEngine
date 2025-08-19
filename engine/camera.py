import pygame
from typing import Optional, Tuple


class Camera:
    """2D camera with smooth follow and coordinate transforms."""

    def __init__(self, viewport_width: int, viewport_height: int) -> None:
        self.viewport_size = pygame.Vector2(viewport_width, viewport_height)
        self.position = pygame.Vector2(0, 0)  # world top-left
        self._target = None  # type: Optional[object]
        self.smooth_speed_per_second = 8.0
        self.world_bounds: Optional[pygame.Rect] = None

    def set_target(self, target: object) -> None:
        self._target = target

    def set_world_bounds(self, bounds: Optional[pygame.Rect]) -> None:
        self.world_bounds = bounds

    def world_to_screen(self, world_point: Tuple[float, float]) -> Tuple[int, int]:
        p = pygame.Vector2(world_point) - self.position
        return int(p.x), int(p.y)

    def screen_to_world(self, screen_point: Tuple[int, int]) -> Tuple[float, float]:
        p = pygame.Vector2(screen_point) + self.position
        return float(p.x), float(p.y)

    def update(self, dt: float) -> None:
        if self._target is None:
            return
        target_pos = getattr(self._target, "position", None)
        if target_pos is None:
            return
        target_center = pygame.Vector2(target_pos)
        desired_top_left = target_center - self.viewport_size / 2
        t = 1.0 - pow(0.5, dt * self.smooth_speed_per_second)
        self.position += (desired_top_left - self.position) * t
        if self.world_bounds is not None:
            max_x = self.world_bounds.width - self.viewport_size.x
            max_y = self.world_bounds.height - self.viewport_size.y
            self.position.x = max(self.world_bounds.left, min(self.position.x, max_x))
            self.position.y = max(self.world_bounds.top, min(self.position.y, max_y))