from __future__ import annotations

import argparse
import os
import pygame
from engine import Game, Scene, GameObject, TileMap


class DummyPlayer(GameObject):
    """Simple marker for previewing camera follow in the editor."""

    def __init__(self, x: float, y: float, color: tuple[int, int, int] = (255, 220, 90)) -> None:
        super().__init__(x, y)
        self.color = color
        self.size = pygame.Vector2(32, 32)

    def draw(self, surface: pygame.Surface) -> None:
        camera = self.scene.camera if self.scene is not None else None
        if camera is None:
            return
        rect = pygame.Rect(int(self.position.x), int(self.position.y), int(self.size.x), int(self.size.y))
        rect.topleft = camera.world_to_screen(rect.topleft)
        pygame.draw.rect(surface, self.color, rect)


def run_editor(map_path: str | None) -> None:
    game = Game(width=1280, height=720, title="Редактор карт — Pygame Engine")
    scene = Scene()

    if map_path and os.path.isfile(map_path):
        tilemap = TileMap.load(map_path)
        scene.add(tilemap)
    else:
        tilemap = scene.add(TileMap(width_in_tiles=150, height_in_tiles=150, tile_size=32))

    # Dummy player to follow
    player = scene.add(DummyPlayer(100, 100))
    scene.camera.set_target(player)

    # Helper overlay: S to save, L to load, arrows/WASD move player
    save_dir = os.path.join(os.getcwd(), "maps")
    os.makedirs(save_dir, exist_ok=True)
    default_path = map_path or os.path.join(save_dir, "map.json")

    def handle_editor_shortcuts(event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                tilemap.save(default_path)
                print(f"Saved: {default_path}")
            elif event.key == pygame.K_l and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                if os.path.isfile(default_path):
                    loaded = TileMap.load(default_path)
                    scene.remove(tilemap)
                    scene.add(loaded)
                    print(f"Loaded: {default_path}")

    # Patch scene to intercept events for save/load
    original_handle_event = scene.handle_event

    def handle_event_with_shortcuts(event: pygame.event.Event) -> None:
        handle_editor_shortcuts(event)
        original_handle_event(event)

    scene.handle_event = handle_event_with_shortcuts  # type: ignore[assignment]

    game.set_scene(scene)
    game.run()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Редактор карт для движка на Pygame")
    parser.add_argument("--map", type=str, default=None, help="Путь к карте JSON для загрузки/сохранения")
    args = parser.parse_args()
    run_editor(args.map)