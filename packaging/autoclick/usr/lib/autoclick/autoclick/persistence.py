import json
from .models import Macro


class MacroPersistence:
    @staticmethod
    def save(macro: Macro, filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(macro.to_dict(), f, indent=2, ensure_ascii=False)

    @staticmethod
    def load(filepath: str) -> Macro:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Macro.from_dict(data)
