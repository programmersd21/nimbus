"""
tests/test_spring.py — Spring Physics Tests
"""

from nimbus.animation import SPRING_BOUNCY, SPRING_SNAPPY, Spring


def test_spring_initialization() -> None:
    """Test spring initialization."""
    spring = Spring(0.0, stiffness=100, damping=10)
    assert spring.value == 0.0
    assert spring.target == 0.0
    assert spring.velocity == 0.0
    assert spring.stiffness == 100
    assert spring.damping == 10


def test_spring_set_target() -> None:
    """Test setting spring target."""
    spring = Spring(0.0)
    spring.set_target(100.0)
    assert spring.target == 100.0
    assert spring.value == 0.0  # Value doesn't change immediately


def test_spring_snap() -> None:
    """Test snap operation."""
    spring = Spring(0.0)
    spring.set_target(100.0)
    spring.snap(50.0)
    assert spring.value == 50.0
    assert spring.target == 50.0
    assert spring.velocity == 0.0


def test_spring_tick() -> None:
    """Test animation tick."""
    spring = Spring(0.0)
    spring.set_target(100.0)

    # Tick a few times
    for _ in range(60):
        spring.tick(0.016)

    # Value should move toward target
    assert spring.value > 0.0
    assert spring.value < 100.0


def test_spring_settled() -> None:
    """Test settled detection."""
    spring = Spring(100.0)
    spring.set_target(100.0)
    assert spring.settled()

    spring.set_target(200.0)
    assert not spring.settled()

    # Animate until settled
    for _ in range():
        spring.tick(0.016)
        if spring.settled():
            break

    assert spring.settled()
    assert abs(spring.value - 200.0) < 1.0


def test_spring_impulse() -> None:
    """Test impulse operation."""
    spring = Spring(50.0)
    spring.set_target(50.0)
    spring.impulse(10.0)
    assert spring.velocity == 10.0


def test_spring_presets() -> None:
    """Test spring presets."""
    snappy = Spring(0.0, **SPRING_SNAPPY._asdict())
    bouncy = Spring(0.0, **SPRING_BOUNCY._asdict())

    assert snappy.stiffness > bouncy.stiffness  # Snappy is stiffer
    assert snappy.damping > bouncy.damping  # Snappy is more damped
