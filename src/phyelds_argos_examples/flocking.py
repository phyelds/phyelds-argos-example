"""Reynolds separation, cohesion and compass-heading alignment."""
import math

from phyelds.calculus import aggregate, neighbors
from phyelds.experimental.swarm import Vector, neighbors_vectors
from phyelds.libraries.device import sense, store
from phyelds_argos_examples.common import hue


@aggregate
def main() -> Vector:
    """Cruise at 8 cm/s; LED hue is the robot's heading."""
    heading = Vector(*sense("heading"))
    offsets = neighbors_vectors()
    # Exchange before local loops: iteration counts differ between neighborhoods.
    headings = neighbors(heading)
    separation = Vector()
    for offset in offsets.exclude_self().values():
        distance = offset.length()
        if 0 < distance < 0.6:
            separation -= offset / (distance * distance)
    cohesion = sum(offsets.data.values(), Vector()) / len(offsets.data)
    alignment = sum(headings.data.values(), Vector()) / len(headings.data)
    steer = alignment + cohesion + 0.5 * separation + 0.5 * Vector(*sense("obstacle"))
    store("velocity", steer.normalize() * 0.08)
    angle = math.degrees(math.atan2(heading.y, heading.x))
    store("led", hue(angle + 180))
    store("label", f"{angle:.0f}°")
    return heading
