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
        self.scene: Optional["Scene"] = None

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
        self.camera = None  # type: ignore

    def add(self, obj: GameObject) -> GameObject:
        obj.scene = self
        self.game_objects.append(obj)
        return obj

    def remove(self, obj: GameObject) -> None:
        if obj in self.game_objects:
            self.game_objects.remove(obj)
            obj.scene = None

    def handle_event(self, event: pygame.event.Event) -> None:
        for obj in list(self.game_objects):
            obj.on_event(event)

    def update(self, dt: float) -> None:
        if self.camera is not None:
            self.camera.update(dt)  # type: ignore[attr-defined]
        for obj in list(self.game_objects):
            if obj.active:
                obj.update(dt)

    def draw(self, surface: Surface) -> None:
        for obj in list(self.game_objects):
            if obj.visible:
                obj.draw(surface)