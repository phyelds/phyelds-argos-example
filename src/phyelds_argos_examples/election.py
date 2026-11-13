"""Elect a leader, collect the swarm size and spread the total back."""
from phyelds.argos import label, led
from phyelds.calculus import aggregate
from phyelds.libraries.collect import count_nodes
from phyelds.libraries.device import local_id
from phyelds.libraries.spreading import broadcast, distance_to
from phyelds_argos_examples.common import hue, leader_id


@aggregate
def main() -> tuple[int, int, int]:
    """Return hops, network size and elected UID."""
    elected = leader_id()
    leader = elected == local_id()
    hops = distance_to(leader)
    count = count_nodes(hops)
    total = broadcast(leader, count)
    label.send(f"{int(hops)}/{total}" if hops < float("inf") else f"?/{total}")
    led.send((255, 0, 0) if leader else hue(60 + 30 * min(hops, 7)))
    return int(hops) if hops < float("inf") else -1, total, elected
