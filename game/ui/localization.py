from __future__ import annotations
import json
import os
from typing import Dict


class Localization:
	LOCALES_DIR = os.path.join(os.getcwd(), "locales")

	@classmethod
	def load(cls, preferred_language: str = "ru") -> "Localization":
		path = os.path.join(cls.LOCALES_DIR, f"{preferred_language}.json")
		if not os.path.exists(path):
			os.makedirs(cls.LOCALES_DIR, exist_ok=True)
			# Write minimal Russian locale
			with open(path, "w", encoding="utf-8") as f:
				json.dump({
					"paused": "Пауза",
					"resume": "Продолжить",
					"quit": "Выход",
				}, f, ensure_ascii=False, indent=2)
		with open(path, "r", encoding="utf-8") as f:
			data: Dict[str, str] = json.load(f)
		return Localization(data)

	def __init__(self, table: Dict[str, str]):
		self.table = table

	def tr(self, key: str, default: str | None = None) -> str:
		return self.table.get(key, default if default is not None else key)