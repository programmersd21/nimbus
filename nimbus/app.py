"""
app.py — nimbus Application
Main Qt application lifecycle and font loading.
"""

import logging
import sys
from pathlib import Path

from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QApplication

log = logging.getLogger("nimbus.app")


class NimbusApp:
    """nimbus application container."""

    def __init__(self) -> None:
        self.app = QApplication.instance() or QApplication(sys.argv)
        self._window = None

    def _load_custom_font(self) -> str:
        """Load custom font from assets."""
        # Try multiple possible locations
        possible_paths = [
            Path(__file__).parent.parent.parent / "assets" / "fonts" / "font.ttf",
            Path(".") / "assets" / "fonts" / "font.ttf",
            Path("assets") / "fonts" / "font.ttf",
        ]

        font_path = None
        for path in possible_paths:
            if path.exists():
                font_path = path
                break

        if not font_path:
            log.error("Required font not found in:")
            for path in possible_paths:
                log.error("  - %s", path)
            sys.exit(1)

        font_id = QFontDatabase.addApplicationFont(str(font_path))
        if font_id == -1:
            log.error("Failed to load font: %s", font_path)
            sys.exit(1)

        families = QFontDatabase.applicationFontFamilies(font_id)
        if families:
            log.info("Custom font loaded: %s", families[0])
            return families[0]

        log.error("Could not determine font family from: %s", font_path)
        sys.exit(1)

    def run(self) -> int:
        """Run the application."""
        try:
            # Load custom font
            font_family = self._load_custom_font()

            # Import here after QApplication is created
            from nimbus.window import NimbusWindow

            # Create and show window
            self._window = NimbusWindow(font_family=font_family)
            self._window.show()

            log.info("nimbus started successfully")
            return self.app.exec()

        except Exception as e:
            log.exception("Failed to start nimbus: %s", e)
            return 1


def main() -> None:
    """Entry point."""
    app = NimbusApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
