"""
input.py — nimbus Input Handling
Manages keyboard, mouse, and touch input events.
"""

from collections.abc import Callable
from enum import Enum


class InputEvent(Enum):
    """Input event types."""

    MOUSE_ENTER = "mouse_enter"
    MOUSE_LEAVE = "mouse_leave"
    MOUSE_PRESS = "mouse_press"
    MOUSE_RELEASE = "mouse_release"
    MOUSE_DRAG = "mouse_drag"
    KEY_PRESS = "key_press"
    CONTEXT_MENU = "context_menu"


class InputHandler:
    """Centralized input event dispatcher."""

    def __init__(self) -> None:
        self._listeners: dict[InputEvent, list[Callable[[dict[str, object]], None]]] = {
            event: [] for event in InputEvent
        }

    def subscribe(self, event: InputEvent, callback: Callable[[dict[str, object]], None]) -> None:
        """Subscribe to an input event."""
        self._listeners[event].append(callback)

    def unsubscribe(self, event: InputEvent, callback: Callable[[dict[str, object]], None]) -> None:
        """Unsubscribe from an input event."""
        if callback in self._listeners[event]:
            self._listeners[event].remove(callback)

    def dispatch(self, event: InputEvent, data: dict[str, object]) -> None:
        """Dispatch an input event to all subscribers."""
        for callback in self._listeners[event]:
            callback(data)
