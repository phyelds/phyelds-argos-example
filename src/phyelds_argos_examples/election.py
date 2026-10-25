"""Elect a leader, collect the swarm size and spread the total back."""
from phyelds.calculus import aggregate
from phyelds.libraries.collect import count_nodes
from phyelds.libraries.device import local_id, store
from phyelds.libraries.spreading import broadcast, distance_to
from phyelds_argos_examples.common import hue, leader_id


@aggregate
def main() -> tuple[int, int, int]:
    """Return hops, network size and elected UID."""
    elected = leader_id()
    leader = elected == local_id()
    hops = distance_to(leader)
    count = count_nodes(hops)
    total = int(broadcast(leader, count))
    store("label", f"{int(hops)}/{total}" if hops < float("inf") else f"?/{total}")
    store("led", (255, 0, 0) if leader else hue(60 + 30 * min(float(hops), 7)))
    return int(hops) if hops < float("inf") else -1, total, elected
