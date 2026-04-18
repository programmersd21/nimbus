"""
tests/test_state.py — State Machine Tests
"""

import pytest

from nimbus.state import NimbusState, get_geometry, get_spring_preset


def test_state_enum() -> None:
    """Test state enumeration."""
    assert NimbusState.IDLE.value == "idle"
    assert NimbusState.EXPANDED.value == "expanded"
    assert NimbusState.NOTIFICATION.value == "notification"
    assert NimbusState.MEDIA.value == "media"
    assert NimbusState.HIDDEN.value == "hidden"


def test_get_geometry() -> None:
    """Test geometry retrieval."""
    idle_geom = get_geometry(NimbusState.IDLE)
    assert idle_geom.width == 126
    assert idle_geom.height == 34
    assert idle_geom.radius == 17.0

    expanded_geom = get_geometry(NimbusState.EXPANDED)
    assert expanded_geom.width == 360
    assert expanded_geom.height == 116
    assert expanded_geom.radius == 28.0


def test_get_spring_preset() -> None:
    """Test spring preset retrieval."""
    idle_preset = get_spring_preset(NimbusState.IDLE)
    assert idle_preset.stiffness == 480
    assert idle_preset.damping == 36

    expanded_preset = get_spring_preset(NimbusState.EXPANDED)
    assert expanded_preset.stiffness == 380
    assert expanded_preset.damping == 22


def test_pill_geometry_frozen() -> None:
    """Test that PillGeometry is immutable."""
    geom = get_geometry(NimbusState.IDLE)

    # Should raise AttributeError
    with pytest.raises(AttributeError):
        geom.width = 200  # type: ignore
