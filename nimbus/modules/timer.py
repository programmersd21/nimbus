"""
modules/timer.py — nimbus Timer Module
Real countdown timer with visual UI and completion events.
"""

import logging
import time
from collections.abc import Callable

log = logging.getLogger("nimbus.modules.timer")


class TimerModule:
    """Countdown timer for nimbus."""

    def __init__(self) -> None:
        self._duration_sec = 0
        self._elapsed_sec = 0.0
        self._is_running = False
        self._start_time: float | None = None
        self._on_complete: Callable[[], None] | None = None

    def start(self, duration_sec: int) -> None:
        """Start a countdown timer for duration_sec seconds."""
        self._duration_sec = max(1, duration_sec)
        self._elapsed_sec = 0.0
        self._is_running = True
        self._start_time = time.perf_counter()
        log.info("Timer started: %d seconds", self._duration_sec)

    def pause(self) -> None:
        """Pause the timer."""
        if self._is_running:
            self._is_running = False
            log.info("Timer paused")

    def resume(self) -> None:
        """Resume the timer."""
        if not self._is_running and self._elapsed_sec < self._duration_sec:
            self._is_running = True
            self._start_time = time.perf_counter()
            log.info("Timer resumed")

    def stop(self) -> None:
        """Stop and reset the timer."""
        self._is_running = False
        self._elapsed_sec = 0.0
        self._start_time = None
        log.info("Timer stopped")

    def is_running(self) -> bool:
        """Check if timer is active."""
        return self._is_running

    def get_remaining_sec(self) -> int:
        """Get remaining seconds."""
        if not self._is_running:
            return max(0, self._duration_sec - int(self._elapsed_sec))

        elapsed = time.perf_counter() - (self._start_time or time.perf_counter())
        remaining = self._duration_sec - int(self._elapsed_sec + elapsed)
        return max(0, remaining)

    def get_progress(self) -> float:
        """Get progress as 0.0 to 1.0."""
        if self._duration_sec == 0:
            return 0.0
        return min(1.0, self.get_remaining_sec() / self._duration_sec)

    def on_complete(self, callback: Callable[[], None]) -> None:
        """Register callback for timer completion."""
        self._on_complete = callback

    def update(self) -> None:
        """Update timer state (called every frame)."""
        if not self._is_running:
            return

        if self._start_time is None:
            return

        elapsed = time.perf_counter() - self._start_time
        self._elapsed_sec += elapsed
        self._start_time = time.perf_counter()

        # Check for completion
        if self._elapsed_sec >= self._duration_sec:
            self._is_running = False
            log.info("Timer completed")
            if self._on_complete:
                self._on_complete()
