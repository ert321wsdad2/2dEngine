from __future__ import annotations
import collections
import time


class FrameProfiler:
	def __init__(self, window: int = 120):
		self.times_ms = collections.deque(maxlen=window)
		self.last_frame_start = time.perf_counter()

	def begin_frame(self) -> None:
		self.last_frame_start = time.perf_counter()

	def end_frame(self, _frame_limit_ms: int) -> None:
		now = time.perf_counter()
		elapsed_ms = (now - self.last_frame_start) * 1000.0
		self.times_ms.append(elapsed_ms)

	@property
	def avg_ms(self) -> float:
		if not self.times_ms:
			return 0.0
		return sum(self.times_ms) / len(self.times_ms)

	@property
	def fps(self) -> float:
		ms = self.avg_ms
		if ms <= 0.0001:
			return 0.0
		return 1000.0 / ms