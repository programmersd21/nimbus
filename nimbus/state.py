"""
state.py — nimbus State Machine
Defines all UI states and their target geometries for spring animation.
Each state maps to a pill width, height, and corner radius.
"""

from dataclasses import dataclass
from enum import Enum

from nimbus.animation import SPRING_BOUNCY, SPRING_GENTLE, SPRING_SNAPPY, SpringPreset


class NimbusState(Enum):
    """UI state enumeration."""

    IDLE = "idle"  # Compact clock pill
    EXPANDED = "expanded"  # Full info panel
    NOTIFICATION = "notification"  # Alert banner
    MEDIA = "media"  # Now-playing card
    HIDDEN = "hidden"  # Fully collapsed / invisible


@dataclass(frozen=True)
class PillGeometry:
    """Target dimensions for a given state."""

    width: float
    height: float
    radius: float


# State → Geometry Map
STATE_GEOMETRY: dict[NimbusState, PillGeometry] = {
    NimbusState.IDLE: PillGeometry(width=126, height=34, radius=17.0),
    NimbusState.EXPANDED: PillGeometry(width=360, height=116, radius=28.0),
    NimbusState.NOTIFICATION: PillGeometry(width=320, height=82, radius=28.0),
    NimbusState.MEDIA: PillGeometry(width=320, height=96, radius=28.0),
    NimbusState.HIDDEN: PillGeometry(width=90, height=8, radius=4.0),
}

# Spring Presets per Transition
TRANSITION_SPRING: dict[NimbusState, SpringPreset] = {
    NimbusState.IDLE: SPRING_SNAPPY,
    NimbusState.EXPANDED: SPRING_BOUNCY,
    NimbusState.NOTIFICATION: SPRING_GENTLE,
    NimbusState.MEDIA: SPRING_BOUNCY,
    NimbusState.HIDDEN: SPRING_SNAPPY,
}


def get_geometry(state: NimbusState) -> PillGeometry:
    """Get target geometry for a state."""
    return STATE_GEOMETRY[state]


def get_spring_preset(state: NimbusState) -> SpringPreset:
    """Get spring physics preset for a state transition."""
    return TRANSITION_SPRING[state]
