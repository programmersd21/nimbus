"""
modules/clock.py — nimbus Clock Module
Provides formatted time and date strings for rendering.
"""

from datetime import datetime


class ClockModule:
    """Lightweight clock data provider. Call update() every second."""

    def __init__(self):
        self._dt = datetime.now()

    def update(self) -> None:
        self._dt = datetime.now()

    # ── Formatters ────────────────────────────────────────────────────────────

    def get_time(self) -> str:
        """HH:MM — compact idle display."""
        return self._dt.strftime("%H:%M")

    def get_time_with_seconds(self) -> str:
        """HH:MM:SS — expanded display."""
        return self._dt.strftime("%H:%M:%S")

    def get_date_short(self) -> str:
        """Mon, Jan 01 — expanded subtitle."""
        return self._dt.strftime("%a, %b %d")

    def get_date_long(self) -> str:
        """Monday, January 1 — full date."""
        return self._dt.strftime("%A, %B %#d")

    def get_ampm(self) -> str:
        """AM / PM indicator."""
        return self._dt.strftime("%p")

    def get_hour(self) -> int:
        return self._dt.hour

    def get_minute(self) -> int:
        return self._dt.minute

    def get_second(self) -> int:
        return self._dt.second
