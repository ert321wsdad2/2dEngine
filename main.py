import os
import sys
from typing import Tuple

# Configure headless mode audio to avoid errors if SDL_VIDEODRIVER=dummy
if os.environ.get("SDL_VIDEODRIVER") == "dummy":
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from game.core.config import Config
from game.core.input import InputManager
from game.core.time_step import FixedTimeStep
from game.core.camera import Camera
from game.core.profiling import FrameProfiler
from game.world.tilemap import TileMap
from game.world.player import Player
from game.world.enemy import Enemy
from game.world.projectiles import ProjectilePool
from game.world.particles import ParticleSystem
from game.ui.hud import HUD
from game.ui.menus import PauseMenu
from game.ui.localization import Localization
from game.saves.save_manager import SaveManager


def initialize_pygame(window_size: Tuple[int, int], title: str) -> Tuple[pygame.Surface, pygame.Surface]:
    pygame.init()
    pygame.display.set_caption(title)
    screen = pygame.display.set_mode(window_size, pygame.RESIZABLE | pygame.SCALED)
    surface = pygame.Surface(window_size).convert_alpha()
    return screen, surface


def main() -> None:
    window_width, window_height = 1280, 720
    screen, scene_surface = initialize_pygame((window_width, window_height), "Python 2D Game")

    clock = pygame.time.Clock()
    profiler = FrameProfiler()

    # Systems
    config = Config.load_or_create()
    localization = Localization.load(preferred_language=config.settings.get("lang", "ru"))
    input_manager = InputManager(config)

    tile_size = 32
    world_tiles_w, world_tiles_h = 160, 160
    tile_map = TileMap(world_tiles_w, world_tiles_h, tile_size)

    camera = Camera(view_width=window_width, view_height=window_height, world_width=tile_map.pixel_width, world_height=tile_map.pixel_height)

    projectiles = ProjectilePool(max_projectiles=256)
    particles = ParticleSystem(max_particles=512)

    # Entities
    player = Player(spawn_pos=(tile_size * 4, tile_size * 4), input_manager=input_manager, projectiles=projectiles, particles=particles, tile_map=tile_map)

    enemies = [
        Enemy(spawn_pos=(tile_size * 50, tile_size * 40), tile_map=tile_map, target_getter=lambda: player, projectiles=projectiles, particles=particles),
        Enemy(spawn_pos=(tile_size * 80, tile_size * 75), tile_map=tile_map, target_getter=lambda: player, projectiles=projectiles, particles=particles),
    ]

    hud = HUD(localization=localization, config=config)
    pause_menu = PauseMenu(localization=localization, config=config, input_manager=input_manager)

    save_manager = SaveManager()

    time_step = FixedTimeStep(target_fps=60)

    headless_mode = os.environ.get("SDL_VIDEODRIVER") == "dummy"
    frames_in_headless = 0

    running = True
    while running:
        profiler.begin_frame()

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            input_manager.process_event(event)
            pause_menu.process_event(event)

        # Toggle pause
        if input_manager.was_action_pressed("pause"):
            pause_menu.toggle()

        # Window resizes
        if pygame.display.get_window_size() != (window_width, window_height):
            window_width, window_height = pygame.display.get_window_size()
            scene_surface = pygame.Surface((window_width, window_height)).convert_alpha()
            camera.resize_view(window_width, window_height)

        # Update logic with fixed time step
        for _ in time_step.step():
            if not pause_menu.is_open:
                input_manager.update()

                # Update entities
                player.update(camera)
                for enemy in enemies:
                    enemy.update()

                projectiles.update(tile_map=tile_map, player=player, enemies=enemies)
                particles.update()

                # Camera follows player with dead zone and world clamp
                camera.update_follow(player.position)

                # Quick save/load
                if input_manager.was_action_pressed("quicksave"):
                    save_manager.quick_save(player, enemies, tile_map, config)
                if input_manager.was_action_pressed("quickload"):
                    save_manager.quick_load(player, enemies, tile_map, config)

            else:
                # Pause menu interaction while paused
                pause_menu.update()
                if pause_menu.request_quit:
                    running = False

        # Render
        scene_surface.fill((16, 16, 20))

        tile_map.draw(scene_surface, camera)

        # Draw entities
        for enemy in enemies:
            enemy.draw(scene_surface, camera)
        player.draw(scene_surface, camera)

        projectiles.draw(scene_surface, camera)
        particles.draw(scene_surface, camera)

        # UI
        hud.draw(scene_surface, player=player, enemies=enemies, projectiles=projectiles, config=config, profiler=profiler)
        if pause_menu.is_open:
            pause_menu.draw(scene_surface)

        # Present
        screen.blit(scene_surface, (0, 0))
        pygame.display.flip()

        # Cap frame rate
        profiler.end_frame(clock.tick(120))

        # Auto-exit in headless environments to avoid hanging CI
        if headless_mode:
            frames_in_headless += 1
            if frames_in_headless > 120:
                running = False

    # Save on exit
    save_manager.auto_save(player, enemies, tile_map, config)

    pygame.quit()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("Fatal error:", exc)
        pygame.quit()
        sys.exit(1)