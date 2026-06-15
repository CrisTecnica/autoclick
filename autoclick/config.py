import json
import os


CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "autoclick")
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")


DEFAULT_CONFIG = {
    "theme": "dark",
    "start_minimized": False,
    "minimize_to_tray": True,
    "restore_last_macro": False,
    "playback_delay": 0.5,
    "mouse_move_threshold": 5,
    "last_macro_file": "",
    "window_geometry": None,
}


class Config:
    def __init__(self):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        self._data = dict(DEFAULT_CONFIG)
        self._load()

    def _load(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                stored = json.load(f)
                self._data.update(stored)
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def save(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self._data, f, indent=2)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self.save()
