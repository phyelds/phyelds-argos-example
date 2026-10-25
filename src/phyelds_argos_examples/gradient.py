"""Static metric distance gradient from the configured source."""
import math

from phyelds.calculus import aggregate
from phyelds.libraries.device import sense, store
from phyelds.libraries.distances import neighbors_distances
from phyelds.libraries.spreading import distance_to
from phyelds_argos_examples.common import hue


@aggregate
def main() -> float:
    """Colour each robot by its distance along the radio network."""
    source = sense("source")
    distance = float(distance_to(source, neighbors_distances()))
    store("led", (255, 255, 255) if source else hue(min(distance, 6) * 45))
    store("label", f"{int(distance * 100)}cm" if math.isfinite(distance) else "?")
    return distance
