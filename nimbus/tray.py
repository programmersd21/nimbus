"""
tray.py — nimbus System Tray Integration
Provides system tray icon and context menu.
"""

import logging
from collections.abc import Callable

from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

log = logging.getLogger("nimbus.tray")


class NimbusTray:
    """System tray integration for nimbus."""

    def __init__(self) -> None:
        self.tray = QSystemTrayIcon()
        self.menu = QMenu()
        self._setup_menu()

    def _setup_menu(self) -> None:
        """Set up the context menu."""
        show_action = QAction("Show", self.menu)
        hide_action = QAction("Hide", self.menu)
        settings_action = QAction("Settings", self.menu)
        exit_action = QAction("Exit", self.menu)

        self.menu.addAction(show_action)
        self.menu.addAction(hide_action)
        self.menu.addSeparator()
        self.menu.addAction(settings_action)
        self.menu.addSeparator()
        self.menu.addAction(exit_action)

        self.tray.setContextMenu(self.menu)

    def set_icon(self, icon: QIcon) -> None:
        """Set the tray icon."""
        self.tray.setIcon(icon)

    def show(self) -> None:
        """Show the tray icon."""
        self.tray.show()

    def hide(self) -> None:
        """Hide the tray icon."""
        self.tray.hide()

    def on_show(self, callback: Callable[[], None]) -> None:
        """Connect show action."""
        self.menu.actions()[0].triggered.connect(callback)

    def on_hide(self, callback: Callable[[], None]) -> None:
        """Connect hide action."""
        self.menu.actions()[1].triggered.connect(callback)

    def on_exit(self, callback: Callable[[], None]) -> None:
        """Connect exit action."""
        self.menu.actions()[4].triggered.connect(callback)
