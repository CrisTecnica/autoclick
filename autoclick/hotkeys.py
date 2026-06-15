from pynput import keyboard
from PySide6.QtCore import QObject, Signal


HOTKEY_MAP = {
    "<f9>": "record",
    "<f10>": "stop_record",
    "<f11>": "play",
    "<f12>": "stop_all",
    "<esc>": "emergency_stop",
}


DISPLAY_MAP = {
    "record": ("F9", "Gravar"),
    "stop_record": ("F10", "Parar gravação"),
    "play": ("F11", "Reproduzir"),
    "stop_all": ("F12", "Tudo parar"),
    "emergency_stop": ("Esc", "Parada de emergência"),
}


class HotkeyManager(QObject):
    hotkey_triggered = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._listener = None
        self._running = False

    def _make_handler(self, action):
        def handler():
            self.hotkey_triggered.emit(action)
        return handler

    def start(self):
        if self._running:
            return
        self._running = True
        hotkeys = {hk: self._make_handler(act) for hk, act in HOTKEY_MAP.items()}
        self._listener = keyboard.GlobalHotKeys(hotkeys)
        self._listener.start()

    def stop(self):
        self._running = False
        if self._listener:
            self._listener.stop()
            self._listener = None
