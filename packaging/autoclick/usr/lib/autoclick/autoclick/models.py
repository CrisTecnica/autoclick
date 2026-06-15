from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional
from datetime import datetime


class EventType(Enum):
    MOUSE_MOVE = "mouse_move"
    MOUSE_PRESS = "mouse_press"
    MOUSE_RELEASE = "mouse_release"
    MOUSE_SCROLL = "mouse_scroll"
    KEY_DOWN = "key_down"
    KEY_UP = "key_up"


BUTTON_NAMES = {
    "left": "Botão Esquerdo",
    "right": "Botão Direito",
    "middle": "Botão do Meio",
}


@dataclass
class MacroEvent:
    timestamp: float
    event_type: EventType
    x: Optional[int] = None
    y: Optional[int] = None
    button: Optional[str] = None
    pressed: Optional[bool] = None
    dx: Optional[int] = None
    dy: Optional[int] = None
    key: Optional[str] = None

    @property
    def description(self) -> str:
        et = self.event_type
        if et == EventType.MOUSE_MOVE:
            return f"Mouse moveu para ({self.x}, {self.y})"
        elif et == EventType.MOUSE_PRESS:
            name = BUTTON_NAMES.get(self.button, self.button or "?")
            return f"{name} pressionado em ({self.x}, {self.y})"
        elif et == EventType.MOUSE_RELEASE:
            name = BUTTON_NAMES.get(self.button, self.button or "?")
            return f"{name} solto em ({self.x}, {self.y})"
        elif et == EventType.MOUSE_SCROLL:
            return f"Rolagem ({self.dx}, {self.dy}) em ({self.x}, {self.y})"
        elif et == EventType.KEY_DOWN:
            return f"Tecla {self.key} pressionada"
        elif et == EventType.KEY_UP:
            return f"Tecla {self.key} solta"
        return str(self.event_type)

    @property
    def time_str(self) -> str:
        return f"{self.timestamp:.2f}s"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["event_type"] = self.event_type.value
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "MacroEvent":
        d = dict(d)
        d["event_type"] = EventType(d["event_type"])
        return cls(**d)


@dataclass
class Macro:
    version: str = "1.0"
    name: str = "Macro sem título"
    created_at: str = ""
    events: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "name": self.name,
            "created_at": self.created_at or datetime.now().isoformat(),
            "events": [e.to_dict() for e in self.events],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Macro":
        m = cls(
            version=d.get("version", "1.0"),
            name=d.get("name", "Macro sem título"),
            created_at=d.get("created_at", ""),
            events=[MacroEvent.from_dict(e) for e in d.get("events", [])],
        )
        return m
