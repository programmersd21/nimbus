"""
modules/permissions.py — nimbus Privacy/Permission Module
Monitors system-wide microphone and camera access.
"""

import logging
from winrt.windows.security.authorization.appcapabilityaccess import AppCapability

log = logging.getLogger("nimbus.modules.permissions")


class PermissionModule:
    """Monitors system-wide camera and microphone access."""

    def __init__(self):
        self.camera_cap = AppCapability.create("webcam")
        self.mic_cap = AppCapability.create("microphone")

    @property
    def camera_active(self) -> bool:
        try:
            return self.camera_cap.check_access().name == "Allowed"
        except Exception as e:
            log.debug("Error checking camera: %s", e)
            return False

    @property
    def mic_active(self) -> bool:
        try:
            return self.mic_cap.check_access().name == "Allowed"
        except Exception as e:
            log.debug("Error checking mic: %s", e)
            return False
