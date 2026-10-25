"""Colours and forces shared by the five swarm programs."""
import colorsys

from phyelds.calculus import aggregate
from phyelds.data import NeighborhoodField
from phyelds.experimental.swarm import Vector
from phyelds.libraries.device import local_id
from phyelds.libraries.leader_election import candidacy, elect_leader


def hue(degrees: float) -> tuple[int, int, int]:
    """Convert a hue angle to an RGB LED colour."""
    channels = colorsys.hsv_to_rgb((degrees % 360) / 360, 1, 1)
    return tuple(round(channel * 255) for channel in channels)


@aggregate
def leader_id() -> int:
    """Elect the lowest UID within 64 hops (more than these networks' diameter)."""
    return elect_leader(64, strategy=candidacy(-local_id()))


def repulsion(offsets: NeighborhoodField[Vector], radius: float) -> Vector:
    """Push away from neighbors closer than radius, with no attractive spring."""
    force = Vector()
    for offset in offsets.exclude_self().values():
        distance = offset.length()
        if 0 < distance < radius:
            force += offset * (1 - radius / distance)
    return force
