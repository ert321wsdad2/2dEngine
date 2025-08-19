import pygame
from pygame import Surface
from typing import List, Optional, Tuple


class Camera:
    """2D camera with smooth follow and coordinate transforms."""

    def __init__(self, viewport_width: int, viewport_height: int) -> None:
        self.viewport_size = pygame.Vector2(viewport_width, viewport_height)
        self.position = pygame.Vector2(0, 0)  # world top-left
        self._target: Optional["GameObject"] = None
        self.smooth_speed_per_second = 8.0  # higher is snappier
        self.world_bounds: Optional[pygame.Rect] = None

    def set_target(self, target: "GameObject") -> None:
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
        target_center = pygame.Vector2(self._target.position)
        desired_top_left = target_center - self.viewport_size / 2
        # Smoothly interpolate towards desired position
        t = 1.0 - pow(0.5, dt * self.smooth_speed_per_second)
        self.position += (desired_top_left - self.position) * t
        # Clamp to world bounds if set
        if self.world_bounds is not None:
            max_x = self.world_bounds.width - self.viewport_size.x
            max_y = self.world_bounds.height - self.viewport_size.y
            self.position.x = max(self.world_bounds.left, min(self.position.x, max_x))
            self.position.y = max(self.world_bounds.top, min(self.position.y, max_y))


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


class TileMap(GameObject):
    """Simple tile map with optional in-place editing.

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
        # Basic palette: id -> color
        self.palette: dict[int, Tuple[int, int, int]] = {
            1: (86, 176, 76),   # grass
            2: (160, 118, 80),  # dirt
            3: (76, 132, 196),  # water
            4: (120, 120, 120), # stone
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

    def on_event(self, event: pygame.event.Event) -> None:
        super().on_event(event)
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
            if buttons[0]:  # left paint
                self.set_tile(tile_x, tile_y, self.selected_id)
            elif buttons[2]:  # right erase
                self.set_tile(tile_x, tile_y, 0)

    def update(self, dt: float) -> None:
        super().update(dt)

    def draw(self, surface: Surface) -> None:
        camera = self.scene.camera if self.scene is not None else None
        if camera is None:
            return
        tile_size = self.tile_size
        # Determine visible tile bounds
        left = int(max(0, camera.position.x // tile_size))
        top = int(max(0, camera.position.y // tile_size))
        right = int(min(self.width_in_tiles, (camera.position.x + camera.viewport_size.x) // tile_size + 2))
        bottom = int(min(self.height_in_tiles, (camera.position.y + camera.viewport_size.y) // tile_size + 2))
        for ty in range(top, bottom):
            row = self.tiles[ty]
            for tx in range(left, right):
                tid = row[tx]
                if tid == 0:
                    continue
                color = self.palette.get(tid, (255, 0, 255))
                world_x = tx * tile_size
                world_y = ty * tile_size
                screen_x, screen_y = camera.world_to_screen((world_x, world_y))
                rect = pygame.Rect(screen_x, screen_y, tile_size, tile_size)
                pygame.draw.rect(surface, color, rect)


class Scene:
    """A collection of game objects with simple lifecycle management."""

    def __init__(self) -> None:
        self.game_objects: List[GameObject] = []
        self.camera: Optional[Camera] = None

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
            self.camera.update(dt)
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
        camera = self.scene.camera
        cam_pos = (0.0, 0.0)
        target_pos = None
        if camera is not None:
            cam_pos = (camera.position.x, camera.position.y)
            if getattr(camera, "_target", None) is not None:
                target_pos = (camera._target.position.x, camera._target.position.y)
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
        # Render with background boxes for readability
        for text in lines:
            surf = font.render(text, True, (230, 230, 230))
            rect = surf.get_rect(topleft=(8, y))
            # Semi-transparent background using a temporary surface
            pad = 4
            box = pygame.Surface((rect.width + pad * 2, rect.height + pad * 2), pygame.SRCALPHA)
            box.fill(bg)
            self.screen.blit(box, (rect.left - pad, rect.top - pad))
            self.screen.blit(surf, rect)
            y += rect.height + 6