import pygame
from pygame import Surface
from typing import List, Optional


class GameObject:
    """Base game object with position and overridable lifecycle methods."""

    def __init__(self, x: float = 0, y: float = 0) -> None:
        self.position = pygame.Vector2(x, y)
        self.visible = True
        self.active = True
        self.parent: Optional["GameObject"] = None
        self.children: List["GameObject"] = []

    def add_child(self, child: "GameObject") -> None:
        child.parent = self
        self.children.append(child)

    def on_event(self, event: pygame.event.Event) -> None:
        for child in self.children:
            child.on_event(event)

    def update(self, dt: float) -> None:
        for child in self.children:
            if child.active:
                child.update(dt)

    def draw(self, surface: Surface) -> None:
        for child in self.children:
            if child.visible:
                child.draw(surface)


class Scene:
    """A collection of game objects with simple lifecycle management."""

    def __init__(self) -> None:
        self.game_objects: List[GameObject] = []

    def add(self, obj: GameObject) -> GameObject:
        self.game_objects.append(obj)
        return obj

    def remove(self, obj: GameObject) -> None:
        if obj in self.game_objects:
            self.game_objects.remove(obj)

    def handle_event(self, event: pygame.event.Event) -> None:
        for obj in list(self.game_objects):
            obj.on_event(event)

    def update(self, dt: float) -> None:
        for obj in list(self.game_objects):
            if obj.active:
                obj.update(dt)

    def draw(self, surface: Surface) -> None:
        for obj in list(self.game_objects):
            if obj.visible:
                obj.draw(surface)


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
        self._running = False
        self._show_fps = True

    def set_scene(self, scene: Scene) -> None:
        self.scene = scene

    def stop(self) -> None:
        self._running = False

    def run(self) -> None:
        self._running = True
        while self._running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                else:
                    self.scene.handle_event(event)

            dt = self.clock.tick(self.target_fps) / 1000.0

            self.scene.update(dt)

            self.screen.fill(self.background_color)
            self.scene.draw(self.screen)

            if self._show_fps:
                self._draw_fps_overlay()

            pygame.display.flip()

        pygame.quit()

    def _draw_fps_overlay(self) -> None:
        fps = self.clock.get_fps()
        font = pygame.font.SysFont("consolas", 16)
        text = font.render(f"{fps:5.1f} FPS", True, (180, 180, 180))
        self.screen.blit(text, (8, 8))