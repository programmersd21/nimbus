"""
renderer.py — Nimbus Rendering Pipeline
"""

import time

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
)
from nimbus.core.state import NimbusState

C_PILL = QColor(10, 10, 10, 238)
C_TEXT = QColor(255, 255, 255, 255)
C_TEXT_DIM = QColor(255, 255, 255, 150)
C_TEXT_HINT = QColor(255, 255, 255, 80)
C_BORDER = QColor(255, 255, 255, 12)
C_ACCENT_GREEN = QColor(80, 210, 100)
C_ACCENT_BLUE = QColor(60, 130, 255)
C_ACCENT_PURPLE = QColor(160, 100, 255)
C_ACCENT_ORANGE = QColor(255, 160, 50)
C_SHADOW = QColor(0, 0, 0)

CANVAS = 420


def _font(family: str, size: int, weight=QFont.Weight.Medium, italic: bool = False) -> QFont:
    f = QFont(family, size)
    f.setWeight(weight)
    f.setItalic(italic)
    return f


class NimbusRenderer:
    def __init__(self, font_family: str = "Segoe UI"):
        self.font_family = font_family

    def paint(
        self,
        painter,
        *,
        w,
        h,
        r,
        opacity,
        state,
        clock,
        media,
        notifications,
        status,
        permissions,
        content_alpha=1.0,
    ):
        painter.save()
        painter.setRenderHints(
            QPainter.RenderHint.Antialiasing
            | QPainter.RenderHint.TextAntialiasing
            | QPainter.RenderHint.SmoothPixmapTransform
        )
        cx, top = CANVAS / 2, 24.0
        pill = QRectF(cx - w / 2, top, w, h)
        painter.setOpacity(opacity)
        self._draw_shadow(painter, pill, r)
        self._draw_pill_body(painter, pill, r)
        if content_alpha > 0.01:
            painter.setOpacity(opacity * content_alpha)
            self._draw_content(painter, pill, state, clock, media, notifications, status, permissions)
        painter.restore()

    def _draw_shadow(self, painter, pill, r):
        shadow = pill.adjusted(0, 4, 0, 4)
        path = QPainterPath()
        path.addRoundedRect(shadow, r, r)
        painter.fillPath(path, QColor(0, 0, 0, 40))

    def _draw_pill_body(self, painter, pill, r):
        path = QPainterPath()
        path.addRoundedRect(pill, r, r)
        grad = QLinearGradient(pill.topLeft(), pill.bottomLeft())
        grad.setColorAt(0.0, QColor(22, 22, 22, 238))
        grad.setColorAt(0.5, QColor(10, 10, 10, 240))
        grad.setColorAt(1.0, QColor(6, 6, 6, 242))
        painter.fillPath(path, grad)
        painter.setPen(QPen(QColor(255, 255, 255, 20), 0.8))
        painter.drawPath(path)

    def _draw_content(self, painter, pill, state, clock, media, notifications, status, permissions):
        clip = QPainterPath()
        clip.addRoundedRect(pill, 17, 17)
        painter.setClipPath(clip)
        if state == NimbusState.IDLE:
            self._draw_text_centered(
                painter,
                pill,
                clock.get_time(),
                _font(self.font_family, 14, QFont.Weight.Medium),
                C_TEXT,
            )
        elif state == NimbusState.MEDIA:
            self._draw_media_compact(painter, pill, media)
        elif state == NimbusState.STATS_CPU:
            self._draw_stats_micro(painter, pill, "CPU", status.cpu_percent, C_ACCENT_BLUE)
        elif state == NimbusState.STATS_RAM:
            self._draw_stats_micro(painter, pill, "RAM", status.ram_percent, C_ACCENT_PURPLE)
        elif state == NimbusState.STATS_SSD:
            self._draw_stats_micro(painter, pill, "SSD", status.ssd_percent, C_ACCENT_ORANGE)
        elif state == NimbusState.STATS_PRIVACY:
            self._draw_privacy_micro(painter, pill, permissions)
        elif state == NimbusState.EXPANDED:
            self._draw_expanded(painter, pill, clock, media, permissions)
        elif state == NimbusState.BIG_STATS:
            self._draw_big_stats(painter, pill, status)
        elif state == NimbusState.NOTIFICATION:
            self._draw_notification(painter, pill, notifications)
        painter.setClipping(False)

    def _draw_text_centered(self, painter, rect, text, font, color):
        painter.setFont(font)
        painter.setPen(color)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, text)

    def _draw_visualizer(self, painter, pill, media, rect):
        bar_w, bar_gap, bars = 3.0, 2.5, media.get_bar_heights()
        total_w = len(bars) * bar_w + (len(bars) - 1) * bar_gap
        bx, by_base = rect.right() - total_w, rect.bottom()
        for i, bar_h in enumerate(bars):
            path = QPainterPath()
            path.addRoundedRect(
                QRectF(bx + i * (bar_w + bar_gap), by_base - bar_h, bar_w, bar_h), 1.5, 1.5
            )
            painter.fillPath(path, C_ACCENT_GREEN if media.is_playing() else C_TEXT_HINT)

    def _draw_media_compact(self, painter, pill, media):
        thumb_r, pad = 11.0, 6.0
        cx, cy = pill.left() + pad + thumb_r, pill.center().y()
        painter.setBrush(QColor(80, 50, 180))
        painter.drawEllipse(QPointF(cx, cy), thumb_r, thumb_r)

        full_text = f"{media.get_title()} • {media.get_artist()}"
        # Adjust text rect to leave room for visualizer on the right
        text_rect = QRectF(
            cx + thumb_r + 10, pill.top(), pill.right() - (cx + thumb_r + 45), pill.height()
        )
        self._draw_scrolling_text(painter, text_rect, full_text, _font(self.font_family, 10))

        # Gap of 5px + visualizer
        vis_rect = QRectF(pill.right() - 35, pill.top() + 10, 25, 15)
        self._draw_visualizer(painter, pill, media, vis_rect)

    def _draw_stats_micro(self, painter, pill, label, val, color):
        painter.setFont(_font(self.font_family, 10, QFont.Weight.Bold))
        painter.setPen(C_TEXT_HINT)
        painter.drawText(pill.adjusted(12, 0, 0, 0), Qt.AlignmentFlag.AlignVCenter, label)
        painter.setPen(C_TEXT)
        painter.drawText(
            pill.adjusted(0, 0, -12, 0),
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
            f"{int(val)}%",
        )
        bar_w, bar_h = 40.0, 4.0
        bx, by = pill.center().x() - bar_w / 2, pill.center().y() - bar_h / 2

        # Background bar
        painter.setBrush(QColor(255, 255, 255, 20))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(bx, by, bar_w, bar_h, 2, 2)

        # Value bar
        painter.setBrush(color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(bx, by, bar_w * (val / 100.0), bar_h, 2, 2)

    def _draw_big_stats(self, painter, pill, status):
        pad = 24.0
        painter.setFont(_font(self.font_family, 14, QFont.Weight.Bold))
        painter.setPen(C_TEXT)
        painter.drawText(pill.adjusted(pad, pad, -pad, 0), "System Resources")
        gw, gh = pill.width() - pad * 2, (pill.height() - pad * 3 - 30) / 3
        self._draw_graph(
            painter,
            QRectF(pill.left() + pad, pill.top() + pad + 25, gw, gh),
            "CPU",
            status.cpu_percent,
            status.get_cpu_history(),
            C_ACCENT_BLUE,
        )
        self._draw_graph(
            painter,
            QRectF(pill.left() + pad, pill.top() + pad + gh + 40, gw, gh),
            "RAM",
            status.ram_percent,
            status.get_ram_history(),
            C_ACCENT_PURPLE,
        )
        self._draw_graph(
            painter,
            QRectF(pill.left() + pad, pill.top() + pad + gh * 2 + 55, gw, gh),
            "SSD",
            status.ssd_percent,
            status.get_ssd_history(),
            C_ACCENT_ORANGE,
        )

    def _draw_scrolling_text(self, painter, rect, text, font):
        fm = QFontMetrics(font)
        tw = fm.horizontalAdvance(text)
        if tw <= rect.width():
            painter.setFont(font)
            painter.setPen(C_TEXT)
            painter.drawText(rect, Qt.AlignmentFlag.AlignVCenter, text)
            return
        _speed, offset = 35.0, (time.time() * 35.0) % (tw + 50)
        painter.save()
        painter.setClipRect(rect)
        painter.setFont(font)
        painter.setPen(C_TEXT)
        painter.drawText(
            QPointF(rect.left() - offset, rect.center().y() + fm.ascent() / 2 - 1), text
        )
        painter.drawText(
            QPointF(rect.left() - offset + tw + 50, rect.center().y() + fm.ascent() / 2 - 1), text
        )
        painter.restore()

    def _draw_graph(self, painter, rect, label, percent, history, color):
        painter.setFont(_font(self.font_family, 9, QFont.Weight.DemiBold))
        painter.setPen(C_TEXT_HINT)
        painter.drawText(rect.topLeft() + QPointF(0, 8), label)
        painter.setPen(C_TEXT)
        painter.drawText(rect.topRight() + QPointF(-35, 8), f"{int(percent)}%")
        g_rect = rect.adjusted(0, 14, 0, 0)
        if not history:
            return
        path = QPainterPath()
        step = g_rect.width() / (len(history) - 1)
        for i, v in enumerate(history):
            vx, vy = g_rect.left() + i * step, g_rect.bottom() - (v / 100.0) * g_rect.height()
            if i == 0:
                path.moveTo(vx, vy)
            else:
                path.lineTo(vx, vy)
        fill = QPainterPath(path)
        fill.lineTo(g_rect.right(), g_rect.bottom())
        fill.lineTo(g_rect.left(), g_rect.bottom())
        fill.closeSubpath()
        grad = QLinearGradient(g_rect.topLeft(), g_rect.bottomLeft())
        grad.setColorAt(0, QColor(color.red(), color.green(), color.blue(), 60))
        grad.setColorAt(1, Qt.GlobalColor.transparent)
        painter.fillPath(fill, grad)
        painter.setPen(
            QPen(
                color, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin
            )
        )
        painter.drawPath(path)

    def _draw_expanded(self, painter, pill, clock, media, permissions):
        pad, div_x = 20.0, pill.left() + pill.width() * 0.45
        self._draw_text_centered(
            painter,
            QRectF(pill.left() + pad, pill.top(), div_x - pill.left() - pad, pill.height()),
            clock.get_time(),
            _font(self.font_family, 32, QFont.Weight.Light),
            C_TEXT,
        )
        painter.setPen(QPen(QColor(255, 255, 255, 15), 1))
        painter.drawLine(QPointF(div_x, pill.top() + 20), QPointF(div_x, pill.bottom() - 20))
        m_rect = QRectF(div_x + 20, pill.top() + 20, pill.right() - div_x - 40, pill.height() - 40)
        
        # Privacy Stats
        painter.setFont(_font(self.font_family, 10, QFont.Weight.Medium))
        painter.setPen(C_ACCENT_GREEN if permissions.camera_active else C_TEXT_HINT)
        painter.drawText(m_rect.topLeft(), "CAM")
        painter.setPen(C_ACCENT_GREEN if permissions.mic_active else C_TEXT_HINT)
        painter.drawText(m_rect.topLeft() + QPointF(40, 0), "MIC")

        # Scrolling Title
        title_rect = QRectF(m_rect.left(), m_rect.top() + 25, m_rect.width(), 20)
        self._draw_scrolling_text(
            painter,
            title_rect,
            media.get_title(),
            _font(self.font_family, 12, QFont.Weight.DemiBold),
        )

        # Scrolling Artist
        artist_rect = QRectF(m_rect.left(), m_rect.top() + 45, m_rect.width(), 20)
        self._draw_scrolling_text(
            painter, artist_rect, media.get_artist(), _font(self.font_family, 10)
        )

    def _draw_privacy_micro(self, painter, pill, permissions):
        painter.setFont(_font(self.font_family, 10, QFont.Weight.Bold))
        painter.setPen(C_TEXT_HINT)
        painter.drawText(pill.adjusted(12, 0, 0, 0), Qt.AlignmentFlag.AlignVCenter, "PRIVACY")
        
        # CAM
        painter.setPen(C_ACCENT_GREEN if permissions.camera_active else C_TEXT_HINT)
        painter.drawText(pill.adjusted(0, 0, -45, 0), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, "CAM")
        
        # MIC
        painter.setPen(C_ACCENT_GREEN if permissions.mic_active else C_TEXT_HINT)
        painter.drawText(pill.adjusted(0, 0, -12, 0), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight, "MIC")

    def _draw_notification(self, painter, pill, notifications):
        """Draw latest notification with scrolling title."""
        notif = notifications.get_current()
        if not notif:
            # Show placeholder if no notification
            painter.setFont(_font(self.font_family, 11, QFont.Weight.Medium))
            painter.setPen(C_TEXT_HINT)
            painter.drawText(pill, Qt.AlignmentFlag.AlignCenter, "No notifications")
            return
        
        pad = 14.0
        # App name + timestamp at top
        painter.setFont(_font(self.font_family, 9, QFont.Weight.DemiBold))
        painter.setPen(C_TEXT_HINT)
        app_time_text = f"{notif.app} • {notif.time_str()}"
        painter.drawText(pill.adjusted(pad, pad, -pad, 0), Qt.AlignmentFlag.AlignTop, app_time_text)
        
        # Title with scrolling (main content)
        title_rect = QRectF(
            pill.left() + pad,
            pill.top() + pad + 16,
            pill.width() - pad * 2,
            20
        )
        painter.setFont(_font(self.font_family, 12, QFont.Weight.DemiBold))
        self._draw_scrolling_text(painter, title_rect, notif.title, _font(self.font_family, 12, QFont.Weight.DemiBold))
        
        # Body with scrolling
        body_rect = QRectF(
            pill.left() + pad,
            pill.top() + pad + 38,
            pill.width() - pad * 2,
            pill.height() - pad * 3 - 38
        )
        painter.setFont(_font(self.font_family, 10))
        self._draw_scrolling_text(painter, body_rect, notif.truncated_body(), _font(self.font_family, 10))

    def _elide(self, font, text, max_w):
        return QFontMetrics(font).elidedText(text, Qt.TextElideMode.ElideRight, int(max_w))
