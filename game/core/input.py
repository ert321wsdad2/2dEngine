from __future__ import annotations
import pygame
from typing import Dict, List, Set, Tuple

from .config import Config


def _key_name_to_constant(name: str) -> int | None:
    if name.startswith("K_"):
        return getattr(pygame, name, None)
    return None


class InputManager:
    def __init__(self, config: Config):
        self.config = config
        self._bindings: Dict[str, List[str]] = dict(config.settings.get("input", {}))

        # State
        self._pressed_actions: Set[str] = set()
        self._released_actions: Set[str] = set()
        self._held_actions: Set[str] = set()

        self._move_axis: Tuple[float, float] = (0.0, 0.0)
        self._mouse_pos: Tuple[int, int] = (0, 0)
        self._mouse_buttons: Tuple[int, int, int] = (0, 0, 0)

        # Gamepad
        pygame.joystick.init()
        self._joystick = pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None
        if self._joystick is not None:
            self._joystick.init()

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
            key = event.key
            is_down = event.type == pygame.KEYDOWN
            self._apply_key_event(key, is_down)
        elif event.type == pygame.MOUSEMOTION:
            self._mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._mouse_buttons = pygame.mouse.get_pressed(3)
            if event.button == 1:
                self._pressed_actions.add("fire")
                self._held_actions.add("fire")
        elif event.type == pygame.MOUSEBUTTONUP:
            self._mouse_buttons = pygame.mouse.get_pressed(3)
            if event.button == 1:
                self._released_actions.add("fire")
                if "fire" in self._held_actions:
                    self._held_actions.remove("fire")
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:
                self._pressed_actions.add("fire")
                self._held_actions.add("fire")
        elif event.type == pygame.JOYBUTTONUP:
            if event.button == 0:
                self._released_actions.add("fire")
                if "fire" in self._held_actions:
                    self._held_actions.remove("fire")

    def _apply_key_event(self, key: int, is_down: bool) -> None:
        for action, names in self._bindings.items():
            for name in names:
                const = _key_name_to_constant(name)
                if const is None:
                    continue
                if const == key:
                    if is_down:
                        self._pressed_actions.add(action)
                        self._held_actions.add(action)
                    else:
                        self._released_actions.add(action)
                        if action in self._held_actions:
                            self._held_actions.remove(action)

    def update(self) -> None:
        # Compute move axis from keyboard
        keys = pygame.key.get_pressed()
        up = self._is_action_held("move_up", keys)
        down = self._is_action_held("move_down", keys)
        left = self._is_action_held("move_left", keys)
        right = self._is_action_held("move_right", keys)

        x = 0.0
        y = 0.0
        if left:
            x -= 1.0
        if right:
            x += 1.0
        if up:
            y -= 1.0
        if down:
            y += 1.0

        # Gamepad axes
        if self._joystick is not None:
            ax_x = self._joystick.get_axis(0) if self._joystick.get_numaxes() > 0 else 0.0
            ax_y = self._joystick.get_axis(1) if self._joystick.get_numaxes() > 1 else 0.0
            dead = 0.2
            if abs(ax_x) > dead:
                x = ax_x
            if abs(ax_y) > dead:
                y = ax_y

        # Normalize diagonal
        length_sq = x * x + y * y
        if length_sq > 1.0:
            import math
            length = math.sqrt(length_sq)
            x /= length
            y /= length

        self._move_axis = (x, y)

    def end_frame(self) -> None:
        self._pressed_actions.clear()
        self._released_actions.clear()

    def get_move_vector(self) -> Tuple[float, float]:
        return self._move_axis

    def was_action_pressed(self, action: str) -> bool:
        return action in self._pressed_actions

    def is_action_held(self, action: str) -> bool:
        return action in self._held_actions

    def was_action_released(self, action: str) -> bool:
        return action in self._released_actions

    def get_mouse_screen(self) -> Tuple[int, int]:
        return self._mouse_pos

    def _is_action_held(self, action: str, keys) -> bool:
        # Keys may be None in headless tests; guard
        names = self._bindings.get(action, [])
        for name in names:
            const = _key_name_to_constant(name)
            if const is not None and keys[const]:
                return True
        return False