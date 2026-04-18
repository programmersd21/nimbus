"""
layout.py — nimbus Geometry Management
Handles pill positioning, layout calculations, and responsive sizing.
"""

from dataclasses import dataclass

from PySide6.QtCore import QRect


@dataclass
class Layout:
    """Layout helper for pill positioning and sizing."""

    canvas_width: int = 420
    canvas_height: int = 420
    top_margin: int = 12

    def get_canvas_rect(self) -> QRect:
        """Get the full canvas rectangle."""
        return QRect(0, self.top_margin, self.canvas_width, self.canvas_height)

    def get_pill_center(self) -> tuple[float, float]:
        """Get the center point of the pill on the canvas."""
        return (self.canvas_width / 2, self.canvas_height / 2)

    def get_content_margin(self) -> int:
        """Get internal margin for content inside pill."""
        return 12

    @staticmethod
    def squircle_path(x: float, y: float, w: float, h: float, r: float) -> None:
        """
        Generate a smooth squircle (rounded rect) path.
        This is used by the renderer for the pill shape.
        """
        # Squircle parametric equations create a smooth, iPhone-like curve
