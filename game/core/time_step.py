from typing import Generator
import time


class FixedTimeStep:
    def __init__(self, target_fps: int = 60):
        self.dt = 1.0 / float(target_fps)
        self._accumulator = 0.0
        self._last_time = time.perf_counter()

    def step(self) -> Generator[None, None, None]:
        current_time = time.perf_counter()
        frame_time = current_time - self._last_time
        self._last_time = current_time
        # Avoid spiral of death
        if frame_time > 0.25:
            frame_time = 0.25
        self._accumulator += frame_time
        while self._accumulator >= self.dt:
            self._accumulator -= self.dt
            yield None

    @property
    def alpha(self) -> float:
        # Interpolation alpha (0..1) if needed for render interpolation
        if self.dt <= 0:
            return 1.0
        return self._accumulator / self.dt