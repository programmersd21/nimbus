"""modules/notifications.py — nimbus Notification Module
Real Windows notification integration via PowerShell.
"""

import logging
import threading
import time
import subprocess
import json
import re
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime

log = logging.getLogger("nimbus.modules.notifications")


@dataclass
class Notification:
    """Real Windows system notification."""

    title: str
    body: str
    app: str = "System"
    icon_color: tuple = (60, 130, 255)  # RGB
    timestamp: datetime = field(default_factory=datetime.now)
    ttl_seconds: int = 8

    def time_str(self) -> str:
        return self.timestamp.strftime("%H:%M")

    def truncated_body(self, max_chars: int = 40) -> str:
        if len(self.body) <= max_chars:
            return self.body
        return self.body[: max_chars - 1].rstrip() + "…"

    def is_expired(self) -> bool:
        """Check if notification has expired."""
        age = (datetime.now() - self.timestamp).total_seconds()
        return age > self.ttl_seconds


class NotificationModule:
    """Windows notification listener using Windows notification database."""

    def __init__(self) -> None:
        self._queue: deque[Notification] = deque(maxlen=10)
        self._current: Notification | None = None
        self._lock = threading.Lock()
        self._listener_running = False
        self._last_notif_hash = None
        self._last_notif_time = 0.0
        
        self._start_listener()

    def _start_listener(self) -> None:
        """Start polling for system notifications."""
        try:
            self._listener_running = True
            thread = threading.Thread(target=self._poll_notifications, daemon=True)
            thread.start()
            log.info("Notification listener started")
        except Exception as e:
            log.warning("Failed to start notification listener: %s", e)
            self._listener_running = False

    def _poll_notifications(self) -> None:
        """Background thread polling Windows notifications."""
        try:
            while self._listener_running:
                try:
                    # Try PowerShell approach
                    result = self._get_notification_via_powershell()
                    
                    if result:
                        # Check if this is a new notification (debounce 500ms)
                        current_time = time.time()
                        if current_time - self._last_notif_time > 0.5:
                            self._last_notif_time = current_time
                            
                            notif = Notification(
                                title=result.get("title", "Notification"),
                                body=result.get("body", ""),
                                app=result.get("app", "System"),
                                timestamp=datetime.now()
                            )
                            
                            with self._lock:
                                self._queue.appendleft(notif)
                                self._current = notif
                            
                            log.info("New notification: %s - %s", notif.app, notif.title)
                    
                    time.sleep(1.0)
                except Exception as e:
                    log.debug("Error in notification poll: %s", e)
                    time.sleep(2.0)
        except Exception as e:
            log.warning("Notification listener thread error: %s", e)
            self._listener_running = False

    def _get_notification_via_powershell(self) -> dict | None:
        """Get latest notification from Windows event log."""
        try:
            # Query Windows event log for recent notifications
            ps_script = """
$events = Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-ActionCenter/Operational'} -MaxEvents 1 -ErrorAction SilentlyContinue
if ($events) {
    $xml = [xml]$events[0].ToXml()
    $message = $events[0].Message
    
    # Try to extract title and body from message or properties
    $title = ""
    $body = ""
    $app = "Windows"
    
    # Parse message (format varies by event type)
    if ($message -match "Title:\\s*(.+?)\\s*Body:") {
        $title = $matches[1]
    }
    if ($message -match "Body:\\s*(.+?)(?:\\n|$)") {
        $body = $matches[1]
    }
    
    $result = @{
        title = if ($title) { $title } else { "Notification" }
        body = $body
        app = $app
    }
    $result | ConvertTo-Json
}
"""
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    data = json.loads(result.stdout.strip())
                    return data
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            log.debug("PowerShell query failed: %s", e)
        
        return None

    def _parse_notification_xml(self, xml_str: str) -> tuple[str, str]:
        """Extract title and body text from notification XML."""
        title, body = "", ""
        try:
            # Look for text elements: <text id="0">Title</text>
            text_matches = re.findall(r'<text[^>]*>([^<]+)</text>', xml_str)
            if len(text_matches) > 0:
                title = text_matches[0]
            if len(text_matches) > 1:
                body = text_matches[1]
        except Exception as e:
            log.debug("Error parsing XML: %s", e)
        
        return title, body

    def push(
        self, title: str, body: str, app: str = "System", icon_color: tuple = (60, 130, 255)
    ) -> None:
        """Add a notification to queue (for testing)."""
        notif = Notification(title=title, body=body, app=app, icon_color=icon_color)
        with self._lock:
            self._queue.appendleft(notif)
            self._current = notif
        log.info("Notification pushed: %s", title)

    def get_current(self) -> Notification | None:
        """Get current notification (with expiration check)."""
        with self._lock:
            # Clean expired notifications
            while self._queue and self._queue[0].is_expired():
                self._queue.popleft()
            
            # Prioritize existing _current if still valid
            if self._current and not self._current.is_expired():
                return self._current

            if not self._queue:
                return None

            return self._queue[0]

    def clear_current(self) -> None:
        """Clear current notification."""
        with self._lock:
            self._current = None

    def get_history(self) -> list[Notification]:
        """Get all active notifications."""
        with self._lock:
            return list(self._queue)
        