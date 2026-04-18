"""
state.py — nimbus State Machine
Defines all UI states and their target geometries for spring animation.
Each state maps to a pill width, height, and corner radius.
"""

from dataclasses import dataclass
from enum import Enum


class NimbusState(Enum):
    IDLE = "idle"  # Compact clock pill
    EXPANDED = "expanded"  # Full info panel
    NOTIFICATION = "notification"  # Alert banner
    MEDIA = "media"  # Now-playing card (IDLE variant)
    STATS_CPU = "stats_cpu"  # CPU micro-graph (IDLE variant)
    STATS_RAM = "stats_ram"  # RAM micro-graph (IDLE variant)
    STATS_SSD = "stats_ssd"  # SSD micro-graph (IDLE variant)
    STATS_PRIVACY = "stats_privacy"  # Cam/Mic privacy status (IDLE variant)
    BIG_STATS = "big_stats"  # Large triple graphs (HUGE)
    HIDDEN = "hidden"  # Fully collapsed / invisible


@dataclass(frozen=True)
class PillGeometry:
    """Target dimensions for a given state."""

    width: float
    height: float
    radius: float


# ─── State → Geometry Map ─────────────────────────────────────────────────────

STATE_GEOMETRY: dict[NimbusState, PillGeometry] = {
    NimbusState.IDLE: PillGeometry(width=126, height=34, radius=17.0),
    NimbusState.EXPANDED: PillGeometry(width=360, height=116, radius=28.0),
    NimbusState.NOTIFICATION: PillGeometry(width=320, height=82, radius=28.0),
    NimbusState.MEDIA: PillGeometry(width=200, height=34, radius=17.0),
    NimbusState.STATS_CPU: PillGeometry(width=160, height=34, radius=17.0),
    NimbusState.STATS_RAM: PillGeometry(width=160, height=34, radius=17.0),
    NimbusState.STATS_SSD: PillGeometry(width=160, height=34, radius=17.0),
    NimbusState.STATS_PRIVACY: PillGeometry(width=160, height=34, radius=17.0),
    NimbusState.BIG_STATS: PillGeometry(width=400, height=320, radius=32.0),  # REALLY BIG
    NimbusState.HIDDEN: PillGeometry(width=90, height=8, radius=4.0),
}


# ─── Spring Presets per Transition ───────────────────────────────────────────

TRANSITION_SPRING: dict[NimbusState, dict] = {
    NimbusState.IDLE: {"stiffness": 480, "damping": 36},
    NimbusState.EXPANDED: {"stiffness": 360, "damping": 24},
    NimbusState.NOTIFICATION: {"stiffness": 420, "damping": 28},
    NimbusState.MEDIA: {"stiffness": 420, "damping": 32},
    NimbusState.STATS_CPU: {"stiffness": 420, "damping": 32},
    NimbusState.STATS_RAM: {"stiffness": 420, "damping": 32},
    NimbusState.STATS_SSD: {"stiffness": 420, "damping": 32},
    NimbusState.STATS_PRIVACY: {"stiffness": 420, "damping": 32},
    NimbusState.BIG_STATS: {"stiffness": 280, "damping": 20},  # Smoother for big expansion
    NimbusState.HIDDEN: {"stiffness": 320, "damping": 30},
}


def get_geometry(state: NimbusState) -> PillGeometry:
    return STATE_GEOMETRY[state]


def get_spring_preset(state: NimbusState) -> dict:
    return TRANSITION_SPRING[state]
