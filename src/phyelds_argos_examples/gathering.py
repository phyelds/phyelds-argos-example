"""Gather at the elected leader, integrating radio vectors along a gradient."""
import math

from phyelds.calculus import aggregate
from phyelds.experimental.swarm import Vector, cast_along, neighbors_vectors
from phyelds.libraries.device import local_id, sense, store
from phyelds_argos_examples.common import hue, leader_id, repulsion


@aggregate
def main() -> float:
    """Follow the leader's inferred position, without GPS or direct sight."""
    leader = leader_id() == local_id()
    distance, to_leader = cast_along(leader, Vector(), lambda there, offset: there + offset)
    separation = repulsion(neighbors_vectors(), 0.35)
    velocity = 0.3 * to_leader + 2 * separation + 0.05 * Vector(*sense("obstacle"))
    store("velocity", Vector() if leader else velocity)
    store("led", (255, 0, 0) if leader else hue(min(distance, 3) * 90 + 60))
    store("label", f"{int(to_leader.length() * 100)}cm" if math.isfinite(distance) else "?")
    return to_leader.length()
