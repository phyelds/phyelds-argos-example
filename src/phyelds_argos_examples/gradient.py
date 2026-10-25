"""Static metric distance gradient from the configured source."""
import math

from phyelds.calculus import aggregate
from phyelds.libraries.distances import neighbors_distances
from phyelds.libraries.spreading import distance_to
from phyelds_argos_examples.common import hue
from phyelds_argos_examples.robot import label, led, source


@aggregate
def main() -> float:
    """Colour each robot by its distance along the radio network."""
    is_source = source.sense()
    distance = float(distance_to(is_source, neighbors_distances()))
    led.send((255, 255, 255) if is_source else hue(min(distance, 6) * 45))
    label.send(f"{int(distance * 100)}cm" if math.isfinite(distance) else "?")
    return distance
