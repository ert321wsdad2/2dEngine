from __future__ import annotations

import pygame
from engine import Game, Scene, GameObject


class Player(GameObject):
    def __init__(self, x: float, y: float, color: tuple[int, int, int] = (80, 180, 255)) -> None:
        super().__init__(x, y)
        self.color = color
        self.size = pygame.Vector2(48, 48)
        self.speed_pixels_per_second = 300.0

    def update(self, dt: float) -> None:
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            direction.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            direction.y += 1

        if direction.length_squared() > 0:
            direction = direction.normalize()
        self.position += direction * self.speed_pixels_per_second * dt

        self.position.x = max(0, min(self.position.x, 960 - self.size.x))
        self.position.y = max(0, min(self.position.y, 540 - self.size.y))

    def draw(self, surface: pygame.Surface) -> None:
        rect = pygame.Rect(int(self.position.x), int(self.position.y), int(self.size.x), int(self.size.y))
        pygame.draw.rect(surface, self.color, rect, border_radius=8)


def main() -> None:
    game = Game(width=960, height=540, title="Мини-движок на Pygame")
    scene = Scene()
    scene.add(Player(200, 200))
    game.set_scene(scene)
    game.run()


if __name__ == "__main__":
    main()