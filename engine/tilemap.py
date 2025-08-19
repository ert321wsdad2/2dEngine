import json
import os
import pygame
from pygame import Surface
from typing import List, Tuple

from .core import GameObject


class TileMap(GameObject):
    """Simple tile map with optional in-place editing and save/load to JSON.

    Tile id 0 is considered empty and will not be drawn.
    """

    def __init__(self, width_in_tiles: int, height_in_tiles: int, tile_size: int = 32) -> None:
        super().__init__(0, 0)
        self.tile_size = tile_size
        self.width_in_tiles = width_in_tiles
        self.height_in_tiles = height_in_tiles
        self.tiles: List[List[int]] = [
            [0 for _ in range(width_in_tiles)] for _ in range(height_in_tiles)
        ]
        self.palette: dict[int, Tuple[int, int, int]] = {
            1: (86, 176, 76),
            2: (160, 118, 80),
            3: (76, 132, 196),
            4: (120, 120, 120),
        }
        self.edit_mode = False
        self.selected_id = 1

    def toggle_edit_mode(self) -> None:
        self.edit_mode = not self.edit_mode

    def set_tile(self, tile_x: int, tile_y: int, tile_id: int) -> None:
        if 0 <= tile_x < self.width_in_tiles and 0 <= tile_y < self.height_in_tiles:
            self.tiles[tile_y][tile_x] = tile_id

    def get_tile(self, tile_x: int, tile_y: int) -> int:
        if 0 <= tile_x < self.width_in_tiles and 0 <= tile_y < self.height_in_tiles:
            return self.tiles[tile_y][tile_x]
        return 0

    def handle_editor_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self.toggle_edit_mode()
            if pygame.K_1 <= event.key <= pygame.K_9:
                self.selected_id = event.key - pygame.K_0
        if not self.edit_mode:
            return
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
            buttons = pygame.mouse.get_pressed(3)
            if event.type == pygame.MOUSEMOTION and not any(buttons):
                return
            camera = self.scene.camera if self.scene is not None else None
            if camera is None:
                return
            mouse_pos_screen = pygame.mouse.get_pos()
            world_x, world_y = camera.screen_to_world(mouse_pos_screen)
            tile_x = int(world_x // self.tile_size)
            tile_y = int(world_y // self.tile_size)
            if buttons[0]:
                self.set_tile(tile_x, tile_y, self.selected_id)
            elif buttons[2]:
                self.set_tile(tile_x, tile_y, 0)

    def on_event(self, event: pygame.event.Event) -> None:
        super().on_event(event)
        self.handle_editor_event(event)

    def update(self, dt: float) -> None:
        super().update(dt)

    def draw(self, surface: Surface) -> None:
        camera = self.scene.camera if self.scene is not None else None
        if camera is None:
            return
        ts = self.tile_size
        left = int(max(0, camera.position.x // ts))
        top = int(max(0, camera.position.y // ts))
        right = int(min(self.width_in_tiles, (camera.position.x + camera.viewport_size.x) // ts + 2))
        bottom = int(min(self.height_in_tiles, (camera.position.y + camera.viewport_size.y) // ts + 2))
        for ty in range(top, bottom):
            row = self.tiles[ty]
            for tx in range(left, right):
                tid = row[tx]
                if tid == 0:
                    continue
                color = self.palette.get(tid, (255, 0, 255))
                world_x = tx * ts
                world_y = ty * ts
                screen_x, screen_y = camera.world_to_screen((world_x, world_y))
                rect = pygame.Rect(screen_x, screen_y, ts, ts)
                pygame.draw.rect(surface, color, rect)

    # --- Persistence ---

    def to_dict(self) -> dict:
        return {
            "tile_size": self.tile_size,
            "width_in_tiles": self.width_in_tiles,
            "height_in_tiles": self.height_in_tiles,
            "tiles": self.tiles,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TileMap":
        tilemap = cls(data["width_in_tiles"], data["height_in_tiles"], data["tile_size"])
        tilemap.tiles = data["tiles"]
        return tilemap

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f)

    @classmethod
    def load(cls, path: str) -> "TileMap":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)