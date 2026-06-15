import time
from threading import Lock, Condition
from PySide6.QtCore import QThread, Signal
from pynput import mouse, keyboard
from .models import MacroEvent, EventType
from .capture import Capture


class PlaybackThread(QThread):
    progress = Signal(int)
    event_played = Signal(int, object)
    finished = Signal()
    stopped = Signal()

    def __init__(self, events: list, speed: float = 1.0, parent=None):
        super().__init__(parent)
        self._events = list(events)
        self._speed = speed
        self._paused = False
        self._cancelled = False
        self._lock = Lock()
        self._pause_cond = Condition(self._lock)
        self._mouse_ctrl = mouse.Controller()
        self._keyboard_ctrl = keyboard.Controller()
        self._delay_before = 0.0

    def set_speed(self, speed: float):
        with self._lock:
            self._speed = max(0.1, min(10.0, speed))

    def set_delay_before(self, seconds: float):
        self._delay_before = seconds

    def pause(self):
        with self._lock:
            self._paused = True

    def resume(self):
        with self._lock:
            self._paused = False
            self._pause_cond.notify_all()

    def cancel(self):
        with self._lock:
            self._cancelled = True
            self._paused = False
            self._pause_cond.notify_all()

    def is_paused(self):
        with self._lock:
            return self._paused

    def run(self):
        if self._delay_before > 0:
            if self._check_cancelled():
                return
            time.sleep(self._delay_before)

        for i, event in enumerate(self._events):
            if self._check_cancelled():
                self.stopped.emit()
                return

            self._wait_if_paused()
            if self._cancelled:
                self.stopped.emit()
                return

            if i > 0:
                prev = self._events[i - 1]
                raw_delay = event.timestamp - prev.timestamp
                with self._lock:
                    speed = self._speed
                adjusted = raw_delay / speed
                if adjusted > 0:
                    self._sleep_with_cancel(adjusted)
                    if self._cancelled:
                        self.stopped.emit()
                        return

            self._execute(event)
            self.event_played.emit(i, event)
            self.progress.emit(i + 1)

        if not self._cancelled:
            self.finished.emit()

    def _check_cancelled(self):
        with self._lock:
            return self._cancelled

    def _wait_if_paused(self):
        with self._lock:
            while self._paused and not self._cancelled:
                self._pause_cond.wait(timeout=0.1)

    def _sleep_with_cancel(self, seconds: float):
        interval = 0.05
        elapsed = 0.0
        while elapsed < seconds:
            if self._check_cancelled():
                return
            with self._lock:
                if self._paused:
                    self._wait_if_paused()
            remaining = seconds - elapsed
            chunk = min(interval, remaining)
            if chunk > 0:
                time.sleep(chunk)
            elapsed += chunk

    def _execute(self, event: MacroEvent):
        try:
            et = event.event_type
            if et == EventType.MOUSE_MOVE:
                if event.x is not None and event.y is not None:
                    self._mouse_ctrl.position = (event.x, event.y)

            elif et == EventType.MOUSE_PRESS:
                btn = self._btn(event.button)
                if btn:
                    self._mouse_ctrl.press(btn)

            elif et == EventType.MOUSE_RELEASE:
                btn = self._btn(event.button)
                if btn:
                    self._mouse_ctrl.release(btn)

            elif et == EventType.MOUSE_SCROLL:
                dx = event.dx or 0
                dy = event.dy or 0
                if dx != 0 or dy != 0:
                    self._mouse_ctrl.scroll(dx, dy)

            elif et == EventType.KEY_DOWN:
                k = Capture.parse_key(event.key) if event.key else None
                if k is not None:
                    self._keyboard_ctrl.press(k)

            elif et == EventType.KEY_UP:
                k = Capture.parse_key(event.key) if event.key else None
                if k is not None:
                    self._keyboard_ctrl.release(k)

        except Exception:
            pass

    @staticmethod
    def _btn(name):
        mapping = {
            "left": mouse.Button.left,
            "right": mouse.Button.right,
            "middle": mouse.Button.middle,
        }
        return mapping.get(name)
