"""
main.py — nimbus Entry Point
Bootstraps the Qt application, loads the custom font, creates the window,
and starts the event loop.
"""

import logging
import os
import sys

# ── Logging Setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG,
    format="[%(levelname)s] %(name)s — %(message)s",
)
log = logging.getLogger("nimbus")

# ── Qt ────────────────────────────────────────────────────────────────────────
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication

from nimbus.window import NimbusWindow

# ── Assets ────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(os.path.dirname(BASE_DIR), "assets", "fonts", "font.ttf")


def load_custom_font() -> str | None:
    """
    Load assets/fonts/font.ttf (SF Display Pro or any TTF).
    Returns the family name on success, None on failure.
    """
    if not os.path.exists(FONT_PATH):
        log.warning("Custom font not found at: %s", FONT_PATH)
        log.warning("Drop any TTF (e.g. SF-Pro-Display-Regular.ttf) into assets/fonts/font.ttf")
        return None

    font_id = QFontDatabase.addApplicationFont(FONT_PATH)
    if font_id == -1:
        log.error("Qt could not load font: %s", FONT_PATH)
        return None

    families = QFontDatabase.applicationFontFamilies(font_id)
    if families:
        log.info("Custom font loaded: %s", families[0])
        return families[0]

    return None


import signal


def main() -> int:
    # ── High-DPI ──────────────────────────────────────────────────────────────
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    # Allow Ctrl+C to trigger a graceful exit
    def _handle_exit(sig, frame):
        app = QApplication.instance()
        if app:
            # Find the main window and trigger close
            for widget in app.topLevelWidgets():
                if hasattr(widget, "close"):
                    widget.close()
            # Explicitly quit after close animation
            app.quit()

    signal.signal(signal.SIGINT, _handle_exit)
    app = QApplication(sys.argv)
    app.setApplicationName("nimbus")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("nimbus")
    app.setQuitOnLastWindowClosed(False)

    # Load custom font before creating any widgets
    font_family = load_custom_font()
    if not font_family:
        log.error("Could not load required font at: %s", FONT_PATH)
        sys.exit(1)
    
    log.info("Using loaded font: %s", font_family)

    # ── Window ────────────────────────────────────────────────────────────────
    window = NimbusWindow(font_family=font_family)
    window.show()

    log.info("nimbus is running — right-click the pill for options")
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
