from __future__ import annotations
import json
import os
from typing import List


class SaveManager:
	SAVE_DIR = os.path.join(os.getcwd(), "saves")
	QUICK_PATH = os.path.join(SaveManager.SAVE_DIR, "quick_save.json") if 'SaveManager' in globals() else os.path.join(os.getcwd(), "saves", "quick_save.json")

	def __init__(self):
		os.makedirs(self.SAVE_DIR, exist_ok=True)

	def _serialize(self, player, enemies, tile_map, config) -> dict:
		return {
			"player": {
				"pos": [player.position.x, player.position.y],
				"hp": player.health,
			},
			"enemies": [
				{"pos": [e.position.x, e.position.y], "hp": e.health}
				for e in enemies
			],
			"config": config.settings,
		}

	def _deserialize(self, data: dict, player, enemies, tile_map, config) -> None:
		p = data.get("player", {})
		player.position.xy = p.get("pos", [player.position.x, player.position.y])
		player.health = float(p.get("hp", player.health))
		ens: List[dict] = data.get("enemies", [])
		for i, e in enumerate(enemies):
			if i < len(ens):
				info = ens[i]
				e.position.xy = info.get("pos", [e.position.x, e.position.y])
				e.health = float(info.get("hp", e.health))
		config.settings = data.get("config", config.settings)

	def quick_save(self, player, enemies, tile_map, config) -> None:
		data = self._serialize(player, enemies, tile_map, config)
		with open(self.QUICK_PATH, "w", encoding="utf-8") as f:
			json.dump(data, f, ensure_ascii=False, indent=2)

	def quick_load(self, player, enemies, tile_map, config) -> None:
		if not os.path.exists(self.QUICK_PATH):
			return
		with open(self.QUICK_PATH, "r", encoding="utf-8") as f:
			data = json.load(f)
		self._deserialize(data, player, enemies, tile_map, config)

	def auto_save(self, player, enemies, tile_map, config) -> None:
		self.quick_save(player, enemies, tile_map, config)