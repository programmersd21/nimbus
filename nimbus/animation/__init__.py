"""
animation/spring.py — nimbus Spring Physics Engine
Implements a critically-configurable spring-damper system for smooth,
physics-based UI animations inspired by Apple's Dynamic Island behavior.
"""

from typing import NamedTuple


class SpringPreset(NamedTuple):
    """Named spring physics presets."""

    stiffness: float
    damping: float


SPRING_SNAPPY = SpringPreset(stiffness=480, damping=36)  # Fast, minimal overshoot
SPRING_BOUNCY = SpringPreset(stiffness=380, damping=22)  # Playful, slight bounce
SPRING_GENTLE = SpringPreset(stiffness=180, damping=24)  # Slow, smooth transitions
SPRING_STIFF = SpringPreset(stiffness=700, damping=45)  # Near-instant, very tight


class Spring:
    """
    A spring-damper system simulating real spring physics.

    F = -k * (x - target) - d * v
    where:
        k = stiffness  (spring constant)
        d = damping    (velocity friction)
        x = current value
        v = velocity
    """

    def __init__(self, value: float, stiffness: float = 300.0, damping: float = 30.0) -> None:
        self.value: float = float(value)
        self.velocity: float = 0.0
        self.target: float = float(value)
        self.stiffness: float = stiffness
        self.damping: float = damping

    def tick(self, dt: float) -> None:
        """Advance simulation by dt seconds (use dt ≈ 0.016 at 60 FPS)."""
        # Clamp dt to prevent explosion on lag spikes
        dt = min(dt, 0.05)
        # Sub-step for stability at high stiffness
        steps = 2
        sub_dt = dt / steps
        for _ in range(steps):
            force = -self.stiffness * (self.value - self.target)
            drag = -self.damping * self.velocity
            self.velocity += (force + drag) * sub_dt
            self.value += self.velocity * sub_dt

    def settled(self) -> bool:
        """Returns True when the spring has come to rest."""
        return abs(self.value - self.target) < 0.15 and abs(self.velocity) < 0.15

    def set_target(self, target: float) -> None:
        """Set a new target; spring will animate toward it."""
        self.target = float(target)

    def snap(self, value: float) -> None:
        """Instantly set value and target with no animation."""
        self.value = float(value)
        self.target = float(value)
        self.velocity = 0.0

    def impulse(self, velocity: float) -> None:
        """Apply an instant velocity kick (for tap/bounce effects)."""
        self.velocity += velocity
