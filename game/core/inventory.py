from __future__ import annotations
from typing import List, Dict, Any


class Inventory:
	def __init__(self, capacity: int = 12):
		self.capacity = capacity
		self.slots: List[Dict[str, Any]] = []
		self.currency: int = 0

	def add_currency(self, amount: int) -> None:
		self.currency = max(0, self.currency + int(amount))

	def add_item(self, item: Dict[str, Any]) -> bool:
		if len(self.slots) >= self.capacity:
			return False
		self.slots.append(item)
		return True