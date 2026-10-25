"""The same programs also run without ARGoS, on Device's byte transport."""
import math

import pytest

from phyelds.libraries.device import velocity
from phyelds.vm.device import Device
from phyelds_argos_examples import dispersion, election, flocking, gathering, gradient
from phyelds_argos_examples.robot import heading, label, led, obstacle, source


def run_line(program, size, rounds, spacing=0.5, headings=None):
    devices = [Device(node_id, program, paths="compact") for node_id in range(size)]
    for tick in range(rounds):
        payloads = []
        for node_id, device in enumerate(devices):
            peers = [other for other in (node_id - 1, node_id + 1) if 0 <= other < size]
            payloads.append(device.run_round({
                source.name: node_id == 0, "time": tick / 10,
                "neighbors_distances": {other: spacing for other in peers},
                "neighbors_vectors": {other: ((other - node_id) * spacing, 0, 0) for other in peers},
                heading.name: (1, 0, 0) if headings is None else headings[node_id], obstacle.name: (0, 0, 0),
            }))
        for node_id, payload in enumerate(payloads):
            for other in (node_id - 1, node_id + 1):
                if 0 <= other < size:
                    devices[other].receive(node_id, payload)
    return devices


def test_gradient_uses_measured_path_lengths_without_positions():
    devices = run_line(gradient.main, 5, 15)
    assert [device.result for device in devices] == [0, 0.5, 1, 1.5, 2]
    assert led.read(devices[0].outputs) == (255, 255, 255)


def test_election_counts_the_whole_network_and_elects_the_minimum_id():
    devices = run_line(election.main, 40, 200)
    assert all(device.result[1:] == (40, 0) for device in devices)
    assert label.read(devices[0].outputs) == "0/40"


def test_dispersion_pushes_only_close_neighbors():
    close = run_line(dispersion.main, 2, 5, spacing=0.4)
    far = run_line(dispersion.main, 2, 5, spacing=0.8)
    assert velocity.read(close[0].outputs).x < 0
    assert velocity.read(close[1].outputs).x > 0
    assert all(velocity.read(device.outputs).length() == 0 for device in far)


def test_gathering_integrates_vectors_to_the_leader():
    devices = run_line(gathering.main, 5, 30)
    assert velocity.read(devices[0].outputs).length() == 0
    assert devices[-1].result == pytest.approx(2)
    assert velocity.read(devices[-1].outputs).x < 0


def test_flocking_follows_aligned_headings_at_cruising_speed():
    devices = run_line(flocking.main, 3, 8, spacing=0.7)
    steer = velocity.read(devices[1].outputs)
    assert steer.length() == pytest.approx(0.08)
    assert steer.x > 0 and math.isclose(steer.y, 0)


def test_flocking_aligns_with_peers_with_different_neighborhood_sizes():
    devices = run_line(flocking.main, 3, 8, spacing=0.7, headings=[(0, 1, 0), (1, 0, 0), (0, 1, 0)])
    steer = velocity.read(devices[1].outputs)
    assert steer.y > 0.05
    assert steer.y == pytest.approx(2 * steer.x)
