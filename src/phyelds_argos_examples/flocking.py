"""Reynolds separation, cohesion and compass-heading alignment."""
import math

from phyelds.calculus import aggregate, neighbors
from phyelds.experimental.swarm import Vector, neighbors_vectors
from phyelds.libraries.device import velocity
from phyelds_argos_examples.common import hue
from phyelds_argos_examples.robot import heading, label, led, obstacle


@aggregate
def main() -> Vector:
    """Cruise at 8 cm/s; LED hue is the robot's heading."""
    facing = Vector(*heading.sense())
    offsets = neighbors_vectors()
    # Exchange before local loops: iteration counts differ between neighborhoods.
    headings = neighbors(facing)
    separation = Vector()
    for offset in offsets.exclude_self().values():
        distance = offset.length()
        if 0 < distance < 0.6:
            separation -= offset / (distance * distance)
    cohesion = sum(offsets.data.values(), Vector()) / len(offsets.data)
    alignment = sum(headings.data.values(), Vector()) / len(headings.data)
    steer = alignment + cohesion + 0.5 * separation + 0.5 * Vector(*obstacle.sense())
    velocity.send(steer.normalize() * 0.08)
    angle = math.degrees(math.atan2(facing.y, facing.x))
    led.send(hue(angle + 180))
    label.send(f"{angle:.0f}°")
    return facing
