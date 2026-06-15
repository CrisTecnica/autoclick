import time
from threading import Lock
from pynput import mouse, keyboard
from .models import MacroEvent, EventType


CONTROL_KEYS = {
    keyboard.Key.f9, keyboard.Key.f10,
    keyboard.Key.f11, keyboard.Key.f12,
    keyboard.Key.esc,
}


class Capture:
    def __init__(self, movement_threshold: int = 5):
        self.events: list[MacroEvent] = []
        self._lock = Lock()
        self._start_time = 0.0
        self._mouse_listener = None
        self._keyboard_listener = None
        self._recording = False
        self._movement_threshold = movement_threshold
        self._last_mouse_pos = (0, 0)
        self._last_move_time = 0.0
        self._move_min_interval = 0.016

        self.on_event = None
        self.on_status_change = None

    def set_threshold(self, pixels: int):
        self._movement_threshold = pixels

    def start(self):
        if self._recording:
            return
        self.events.clear()
        self._start_time = time.time()
        self._recording = True
        self._last_mouse_pos = (0, 0)
        self._last_move_time = 0.0

        self._status("gravando")
        self._mouse_listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            on_scroll=self._on_scroll,
        )
        self._keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release,
        )
        self._mouse_listener.start()
        self._keyboard_listener.start()

    def stop(self):
        if not self._recording:
            return
        self._recording = False
        if self._mouse_listener:
            self._mouse_listener.stop()
        if self._keyboard_listener:
            self._keyboard_listener.stop()
        self._status("pronto")

    @property
    def is_recording(self) -> bool:
        return self._recording

    def _ts(self) -> float:
        return time.time() - self._start_time

    def _record(self, event: MacroEvent):
        with self._lock:
            self.events.append(event)
        if self.on_event:
            self.on_event(event)

    def _status(self, msg: str):
        if self.on_status_change:
            self.on_status_change(msg)

    def _on_move(self, x, y):
        if not self._recording:
            return
        now = time.time()
        if (now - self._last_move_time) < self._move_min_interval:
            return
        dx = abs(x - self._last_mouse_pos[0])
        dy = abs(y - self._last_mouse_pos[1])
        if dx < self._movement_threshold and dy < self._movement_threshold:
            return
        self._last_mouse_pos = (x, y)
        self._last_move_time = now
        self._record(MacroEvent(
            timestamp=self._ts(),
            event_type=EventType.MOUSE_MOVE,
            x=x, y=y,
        ))

    def _on_click(self, x, y, button, pressed):
        if not self._recording:
            return
        btn = str(button).replace("Button.", "")
        etype = EventType.MOUSE_PRESS if pressed else EventType.MOUSE_RELEASE
        self._record(MacroEvent(
            timestamp=self._ts(),
            event_type=etype,
            x=x, y=y,
            button=btn,
            pressed=pressed,
        ))

    def _on_scroll(self, x, y, dx, dy):
        if not self._recording:
            return
        self._record(MacroEvent(
            timestamp=self._ts(),
            event_type=EventType.MOUSE_SCROLL,
            x=x, y=y,
            dx=int(dx), dy=int(dy),
        ))

    def _is_control_key(self, key):
        if key in CONTROL_KEYS:
            return True
        key_str = str(key)
        for ck in CONTROL_KEYS:
            if str(ck) == key_str:
                return True
        return False

    def _on_key_press(self, key):
        if not self._recording:
            return
        if self._is_control_key(key):
            return
        self._record(MacroEvent(
            timestamp=self._ts(),
            event_type=EventType.KEY_DOWN,
            key=self._key_str(key),
        ))

    def _on_key_release(self, key):
        if not self._recording:
            return
        if self._is_control_key(key):
            return
        self._record(MacroEvent(
            timestamp=self._ts(),
            event_type=EventType.KEY_UP,
            key=self._key_str(key),
        ))

    @staticmethod
    def _key_str(key):
        if hasattr(key, "char") and key.char:
            return key.char
        if isinstance(key, keyboard.Key):
            return f"Key.{key.name}"
        if hasattr(key, "vk"):
            return f"Vk.{key.vk}"
        return str(key)

    @staticmethod
    def parse_key(key_str: str):
        if key_str.startswith("Key."):
            name = key_str[4:]
            try:
                return keyboard.Key[name]
            except KeyError:
                try:
                    return getattr(keyboard.Key, name)
                except AttributeError:
                    return keyboard.KeyCode.from_char("?")
        elif key_str.startswith("Vk."):
            return keyboard.KeyCode.from_vk(int(key_str[3:]))
        else:
            return keyboard.KeyCode.from_char(key_str)
