"""
modules/media.py — nimbus Media Module
Real Windows media tracking via WinRT SMTC (System Media Transport Controls).
Uses pythoncom to initialize COM apartments in background threads.
"""

import logging
import math
import threading
import time
from dataclasses import dataclass

import pythoncom

log = logging.getLogger("nimbus.modules.media")

try:
    from winrt.windows.media.control import GlobalSystemMediaTransportControlsSessionManager

    WINRT_AVAILABLE = True
except ImportError:
    WINRT_AVAILABLE = False


@dataclass
class Track:
    title: str
    artist: str
    album: str = ""


NONE_TRACK = Track("No Media", "Nothing playing")


class MediaModule:
    """Provides media metadata from Windows SMTC using a dedicated WinRT loop."""

    _BAR_FREQS = [3.1, 4.7, 2.9, 5.3, 3.8]
    _BAR_PHASES = [0.0, 1.2, 2.4, 0.8, 1.9]
    _BAR_COUNT = 5
    _BAR_MIN_H = 3.0
    _BAR_MAX_H = 18.0

    def __init__(self):
        self._lock = threading.Lock()
        self._cached_track = NONE_TRACK
        self._cached_playing = False
        self._manager = None

        if WINRT_AVAILABLE:
            self._stop_event = threading.Event()
            self._worker = threading.Thread(target=self._run_loop, daemon=True)
            self._worker.start()
        else:
            log.warning("WinRT not available; media tracking disabled")

    def _run_loop(self):
        """Worker thread for WinRT with explicit COM initialization."""
        # Initialize COM in this thread to avoid apartment conflicts
        pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)

        while not self._stop_event.is_set():
            try:
                if not self._manager:
                    self._manager = (
                        GlobalSystemMediaTransportControlsSessionManager.request_async().get()
                    )

                session = self._manager.get_current_session()

                if session:
                    props = session.try_get_media_properties_async().get()
                    pb = session.get_playback_info()

                    with self._lock:
                        # 4 is PLAYING
                        self._cached_playing = getattr(pb, "playback_status", 0) == 4
                        self._cached_track = Track(
                            title=getattr(props, "title", "Unknown"),
                            artist=getattr(props, "artist", "Unknown"),
                            album=getattr(props, "album_title", ""),
                        )
                else:
                    with self._lock:
                        self._cached_track = NONE_TRACK
                        self._cached_playing = False
            except Exception as e:
                log.debug("Polling error: %s", e)

            time.sleep(1.0)

        pythoncom.CoUninitialize()

    @property
    def current_track(self):
        with self._lock:
            return self._cached_track

    def get_title(self) -> str:
        return self.current_track.title

    def get_artist(self) -> str:
        return self.current_track.artist

    def get_album(self) -> str:
        return self.current_track.album

    def is_playing(self):
        with self._lock:
            return self._cached_playing

    def toggle_play(self):
        if self._manager and (s := self._manager.get_current_session()):
            s.try_toggle_play_pause_async()

    def next_track(self):
        if self._manager and (s := self._manager.get_current_session()):
            s.try_skip_next_async()

    def prev_track(self):
        if self._manager and (s := self._manager.get_current_session()):
            s.try_skip_previous_async()

    def get_bar_heights(self):
        if not self.is_playing():
            return [self._BAR_MIN_H] * self._BAR_COUNT
        t = time.perf_counter()
        return [
            self._BAR_MIN_H
            + ((math.sin(t * self._BAR_FREQS[i] + self._BAR_PHASES[i]) + 1.0) / 2.0)
            * (self._BAR_MAX_H - self._BAR_MIN_H)
            for i in range(self._BAR_COUNT)
        ]
