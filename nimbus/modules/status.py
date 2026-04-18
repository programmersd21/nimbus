"""
modules/status.py — nimbus System Status Module
Provides live CPU, RAM, and SSD stats with history for beautiful graphing.
"""

import logging
import threading
from collections import deque

import psutil

log = logging.getLogger("nimbus.modules.status")


class StatusModule:
    """System resource tracker for live CPU, RAM, and SSD graphing."""

    def __init__(self, history_len: int = 50):
        self.history_len = history_len
        self._cpu_history = deque([0.0] * history_len, maxlen=history_len)
        self._ram_history = deque([0.0] * history_len, maxlen=history_len)
        self._ssd_history = deque([0.0] * history_len, maxlen=history_len)

        self._last_cpu = 0.0
        self._last_ram = 0.0
        self._last_ssd = 0.0

        self._lock = threading.Lock()
        self._stop_event = threading.Event()

        # Initial SSD usage
        try:
            self._last_ssd = psutil.disk_usage("C:").percent
        except:
            self._last_ssd = 0.0

        # Poll every 500ms
        self._thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._thread.start()

    def _poll_loop(self):
        """Poll system stats periodically."""
        psutil.cpu_percent(interval=None)

        while not self._stop_event.is_set():
            try:
                cpu = psutil.cpu_percent(interval=None)
                ram = psutil.virtual_memory().percent

                # SSD usage (percentage of disk C:)
                try:
                    ssd = psutil.disk_usage("C:").percent
                except:
                    ssd = 0.0

                with self._lock:
                    self._last_cpu = cpu
                    self._last_ram = ram
                    self._last_ssd = ssd
                    self._cpu_history.append(cpu)
                    self._ram_history.append(ram)
                    self._ssd_history.append(ssd)
            except Exception as e:
                log.debug("Stats poll error: %s", e)

            self._stop_event.wait(0.5)

    def stop(self):
        self._stop_event.set()

    # ── Public API ────────────────────────────────────────────────────────────

    @property
    def cpu_percent(self) -> float:
        with self._lock:
            return self._last_cpu

    @property
    def ram_percent(self) -> float:
        with self._lock:
            return self._last_ram

    @property
    def ssd_percent(self) -> float:
        with self._lock:
            return self._last_ssd

    def get_cpu_history(self) -> list[float]:
        with self._lock:
            return list(self._cpu_history)

    def get_ram_history(self) -> list[float]:
        with self._lock:
            return list(self._ram_history)

    def get_ssd_history(self) -> list[float]:
        with self._lock:
            return list(self._ssd_history)
