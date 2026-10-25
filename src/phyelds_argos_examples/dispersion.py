"""Spread a packed swarm with a repulsive spring."""
from phyelds.calculus import aggregate
from phyelds.experimental.swarm import Vector, neighbors_vectors
from phyelds.libraries.device import sense, store
from phyelds_argos_examples.common import repulsion


@aggregate
def main() -> float:
    """Keep 0.6 m between neighbors; green means settled."""
    offsets = neighbors_vectors()
    force = repulsion(offsets, 0.6)
    store("velocity", force + 0.05 * Vector(*sense("obstacle")))
    store("led", (0, 255, 0) if force.length() < 0.02 else (255, 128, 0))
    store("label", str(len(offsets.exclude_self())))
    return force.length()
