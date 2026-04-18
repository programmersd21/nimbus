"""
window.py — nimbus Main Window
"""

import logging
import time

from nimbus.utils.config import load_config
from nimbus.modules import ClockModule, MediaModule, NotificationModule, StatusModule, PermissionModule
from PySide6.QtCore import QPoint, QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QAction, QCursor, QFontDatabase, QPainter
from PySide6.QtWidgets import QApplication, QMenu, QWidget
from nimbus.renderer import CANVAS, NimbusRenderer
from nimbus.core.animation import Spring, SPRING_SNAPPY
from nimbus.core.state import NimbusState, get_geometry, get_spring_preset

log = logging.getLogger("nimbus.window")

# Match the renderer's canvas size
CANVAS_SIZE = CANVAS


class NimbusWindow(QWidget):
    def __init__(self, parent=None, font_family: str | None = None):
        super().__init__(parent)
        self.config = load_config()

        if font_family:
            self._font_family = font_family
        else:
            self._resolve_font()

        # ── State ─────────────────────────────────────────────────────────────
        self._state = NimbusState.IDLE
        self._last_state = NimbusState.IDLE
        self._target_state = NimbusState.IDLE
        self._hover_pill = False

        # State cycle: (IDLE, MEDIA, NOTIFICATION, STATS_CPU, STATS_RAM, STATS_PRIVACY)
        self._cycle_states = [
            NimbusState.IDLE,
            NimbusState.MEDIA,
            NimbusState.NOTIFICATION,
            NimbusState.STATS_CPU,
            NimbusState.STATS_RAM,
            NimbusState.STATS_PRIVACY,
        ]
        self._cycle_idx = 0

        # ── Spring Animations ─────────────────────────────────────────────────
        idle_geo = get_geometry(NimbusState.IDLE)
        self.sp_w = Spring(idle_geo.width, **SPRING_SNAPPY)
        self.sp_h = Spring(idle_geo.height, **SPRING_SNAPPY)
        self.sp_r = Spring(idle_geo.radius, **SPRING_SNAPPY)
        self.sp_opacity = Spring(1.0, stiffness=280, damping=28)
        self.sp_content_alpha = Spring(1.0, stiffness=120, damping=22)

        # ── Modules ───────────────────────────────────────────────────────────
        self.clock = ClockModule()
        self.media = MediaModule()
        self.notifications = NotificationModule()
        self.status = StatusModule()
        self.permissions = PermissionModule()

        # ── Renderer ──────────────────────────────────────────────────────────
        self.renderer = NimbusRenderer(font_family=self._font_family)

        self._setup_window()
        self._center_on_screen()

        # ── Timers ────────────────────────────────────────────────────────────
        self._last_tick = time.perf_counter()

        self._anim_timer = QTimer(self)
        self._anim_timer.setInterval(16)
        self._anim_timer.timeout.connect(self._tick)
        self._anim_timer.start()

        self._clock_timer = QTimer(self)
        self._clock_timer.setInterval(1000)
        self._clock_timer.timeout.connect(self._on_clock_tick)
        self._clock_timer.start()

        self._cycle_timer = QTimer(self)
        self._cycle_timer.setInterval(6000)  # Switch every 6 seconds
        self._cycle_timer.timeout.connect(self._auto_cycle)
        self._cycle_timer.start()

        self._hover_timer = QTimer(self)
        self._hover_timer.setInterval(40)
        self._hover_timer.timeout.connect(self._poll_hover)
        self._hover_timer.start()

        self._collapse_timer = QTimer(self)
        self._collapse_timer.setSingleShot(True)
        self._collapse_timer.timeout.connect(lambda: self.set_state(NimbusState.IDLE))

        self._dragging = False
        self._drag_offset = QPoint()
        self._interactive = False

    def _setup_window(self):
        # Keep WindowStaysOnTopHint for prominence
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setFixedSize(CANVAS_SIZE, CANVAS_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        # Ensure it remains prominent on top
        self.activateWindow()
        self.raise_()

    def _center_on_screen(self):
        screen = QApplication.primaryScreen().virtualGeometry()
        x = screen.left() + (screen.width() - CANVAS_SIZE) // 2
        y = screen.top() - 24
        self.setGeometry(x, y, CANVAS_SIZE, CANVAS_SIZE)

    def set_state(self, new_state: NimbusState) -> None:
        if new_state == self._state:
            return
        self._last_state = self._state
        self._state = new_state
        geo = get_geometry(new_state)
        preset = get_spring_preset(new_state)
        for sp in (self.sp_w, self.sp_h, self.sp_r):
            sp.stiffness = preset["stiffness"]
            sp.damping = preset["damping"]
        self.sp_w.set_target(geo.width)
        self.sp_h.set_target(geo.height)
        self.sp_r.set_target(geo.radius)
        self.sp_opacity.set_target(0.0 if new_state == NimbusState.HIDDEN else 1.0)
        self.sp_content_alpha.snap(0.0)
        self.sp_content_alpha.set_target(1.0)

        delay = self.config.get("auto_collapse_ms", 1000)
        if new_state in (NimbusState.EXPANDED, NimbusState.NOTIFICATION, NimbusState.BIG_STATS):
            self._collapse_timer.start(delay)
        else:
            self._collapse_timer.stop()
        self.update()

    def _tick(self) -> None:
        now = time.perf_counter()
        dt = min(now - self._last_tick, 0.05)
        self._last_tick = now
        changed = False
        for sp in (self.sp_w, self.sp_h, self.sp_r, self.sp_opacity, self.sp_content_alpha):
            if not sp.settled():
                sp.tick(dt)
                changed = True

        # Always repaint if there's scrolling or active animations
        if changed or self._state in (
            NimbusState.MEDIA,
            NimbusState.NOTIFICATION,
            NimbusState.BIG_STATS,
            NimbusState.EXPANDED,
        ):
            self.update()

    def _auto_cycle(self):
        if self._interactive or self._dragging or self._state not in self._cycle_states:
            return
        self._cycle_idx = (self._cycle_idx + 1) % len(self._cycle_states)
        self.set_state(self._cycle_states[self._cycle_idx])

    def _on_clock_tick(self):
        self.clock.update()
        if self._state == NimbusState.IDLE:
            self.update()

    def _poll_hover(self):
        cursor_global = QCursor.pos()
        local = self.mapFromGlobal(cursor_global)
        over_pill = self._hit_test(QPointF(local))
        if over_pill and not self._interactive:
            self._interactive = True
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
            self._collapse_timer.stop()
        elif not over_pill and self._interactive and not self._dragging:
            self._interactive = False
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            if self._state in (NimbusState.EXPANDED, NimbusState.BIG_STATS):
                self._collapse_timer.start(self.config.get("auto_collapse_ms", 1000))

    def _hit_test(self, pos: QPointF) -> bool:
        w = self.sp_w.value
        h = self.sp_h.value
        cx = CANVAS_SIZE / 2
        top = 24.0
        return QRectF(cx - w / 2 - 6, top - 6, w + 12, h + 12).contains(pos)

    def paintEvent(self, _event):
        painter = QPainter(self)
        self.renderer.paint(
            painter,
            w=self.sp_w.value,
            h=self.sp_h.value,
            r=min(self.sp_r.value, self.sp_h.value / 2),
            opacity=max(0.0, min(1.0, self.sp_opacity.value)),
            state=self._state,
            clock=self.clock,
            media=self.media,
            notifications=self.notifications,
            status=self.status,
            permissions=self.permissions,
            content_alpha=max(0.0, min(1.0, self.sp_content_alpha.value)),
        )
        painter.end()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._hit_test(event.position()):
            if self._state in self._cycle_states:
                self.set_state(NimbusState.EXPANDED)
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._hit_test(event.position()):
            if self._state == NimbusState.EXPANDED:
                self.set_state(NimbusState.BIG_STATS)
            elif self._state == NimbusState.BIG_STATS:
                self.set_state(NimbusState.EXPANDED)

    def mouseReleaseEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def _show_context_menu(self, pos):
        menu = QMenu(self)
        menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: rgba(255, 255, 255, 0.08);
                color: #fff;
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 16px;
                padding: 10px;
                background-clip: padding-box;
                font-family: '{self._font_family}';
            }}
            QMenu::item {{
                padding: 10px 30px;
                border-radius: 8px;
                background: transparent;
                font-weight: 500;
            }}
            QMenu::item:selected {{
                background-color: rgba(255, 255, 255, 0.25);
            }}
        """)

        # Collapse action
        collapse_act = QAction("Collapse", self)
        collapse_act.triggered.connect(lambda: self.set_state(NimbusState.IDLE))
        menu.addAction(collapse_act)

        # Quit action
        quit_act = QAction("Quit Nimbus", self)
        quit_act.triggered.connect(self.close)
        menu.addAction(quit_act)

        menu.exec(pos)

    def closeEvent(self, event):
        """Morph exit: slow, dramatic shrink to circle then pop out."""
        # Dramatically shrink
        self.sp_w.set_target(24)
        self.sp_h.set_target(24)
        self.sp_r.set_target(12)
        self.sp_opacity.set_target(0.0)

        # Slower, more prominent animation (300ms -> 500ms)
        end_time = time.time() + 0.5
        while time.time() < end_time:
            self._tick()
            QApplication.processEvents()
            time.sleep(0.01)  # Ensure smoothness

        event.accept()
        QApplication.instance().quit()

    def _resolve_font(self):
        fams = QFontDatabase.families()
        for f in ["SF Pro Display", "SF Pro", "Segoe UI Variable", "Segoe UI"]:
            if f in fams:
                self._font_family = f
                return
        self._font_family = "Segoe UI"
