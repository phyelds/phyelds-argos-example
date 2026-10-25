"""Behavior checks in the real ARGoS physics engine and radio medium."""
import heapq
import math
from pathlib import Path
import re
import subprocess

import pytest

from phyelds.argos.build import build_plugin

ROOT = Path(__file__).resolve().parents[1]
pytestmark = pytest.mark.argos


@pytest.fixture(scope="session")
def observer():
    build_plugin(ROOT / "build", gui=False)
    build = ROOT / "build" / "observer"
    subprocess.run(["cmake", "-S", str(ROOT / "tests/native"), "-B", str(build)], check=True)
    subprocess.run(["cmake", "--build", str(build), "--parallel"], check=True)
    return build / "observer"


@pytest.fixture(scope="session")
def experiments(observer):
    results = {}
    for name in ("gradient", "election", "dispersion", "gathering", "flocking", "mixed_gradient", "mixed_flocking"):
        xml = (ROOT / "experiments" / f"{name}.argos").read_text().replace('length="0"', 'length="30"')
        config = ROOT / "build" / f"{name}.test.argos"
        config.write_text(xml)
        result = subprocess.run(
            [str(observer), str(config)], cwd=ROOT, capture_output=True, text=True, timeout=90, check=False,
        )
        (ROOT / "build" / f"{name}.log").write_text(result.stdout + result.stderr)
        assert result.returncode == 0, result.stdout + result.stderr
        poses = {}
        for line in result.stdout.splitlines():
            if line.startswith("POSE "):
                _, tick, robot, x, y, z, yaw, red, green, blue = line.split()
                pose = (float(x), float(y), float(z), float(yaw), int(red), int(green), int(blue))
                poses.setdefault(int(tick), {})[robot] = pose
        labels = dict(re.findall(r"(\w+) final: (.*)", result.stdout))
        assert poses and labels, result.stdout
        results[name] = (poses, labels)
    return results


def positions(rows):
    return {robot: row[:3] for robot, row in rows.items()}


def nearest_mean(rows):
    points = positions(rows)
    return sum(min(math.dist(point, other) for peer, other in points.items() if peer != robot)
               for robot, point in points.items()) / len(points)


def polarization(rows):
    return math.hypot(sum(math.cos(row[3]) for row in rows.values()),
                      sum(math.sin(row[3]) for row in rows.values())) / len(rows)


@pytest.mark.parametrize("name", ["gradient", "mixed_gradient"])
def test_gradient_matches_shortest_radio_paths(experiments, name):
    poses, labels = experiments[name]
    points = positions(poses[0])
    distances = {robot: float("inf") for robot in points}
    distances["fb0"] = 0
    queue = [(0, "fb0")]
    while queue:
        distance, robot = heapq.heappop(queue)
        if distance > distances[robot]:
            continue
        for peer in points:
            edge = math.dist(points[robot], points[peer])
            if peer != robot and edge <= 0.8 and distance + edge < distances[peer]:
                distances[peer] = distance + edge
                heapq.heappush(queue, (distance + edge, peer))
    for robot, distance in distances.items():
        assert labels[robot] != "?", f"{robot} has no route to fb0"
        assert int(labels[robot][:-2]) / 100 == pytest.approx(distance, abs=0.02)


def test_mixed_gradient_reaches_e_pucks_only_through_eye_bots(experiments):
    points = positions(experiments["mixed_gradient"][0][0])
    assert not any(math.dist(points[foot], points[puck]) <= 0.8
                   for foot in points if foot.startswith("fb") for puck in points if puck.startswith("ep"))


def test_election_reaches_consensus_and_elects_fb0(experiments):
    poses, labels = experiments["election"]
    assert len(labels) == 40
    assert all(label.endswith("/40") for label in labels.values())
    assert labels["fb0"] == "0/40"
    red = [robot for robot, row in poses[300].items() if row[4:] == (255, 0, 0)]
    assert red == ["fb0"]


def test_dispersion_increases_spacing_and_settles(experiments):
    poses, _ = experiments["dispersion"]
    initial, final = nearest_mean(poses[0]), nearest_mean(poses[300])
    assert final > 0.5 and final > initial * 1.5
    assert sum(row[4:] == (0, 255, 0) for row in poses[300].values()) >= 20


def test_gathering_approaches_a_stationary_leader(experiments):
    poses, _ = experiments["gathering"]

    def mean_distance(rows):
        points = positions(rows)
        return sum(math.dist(point, points["fb0"]) for point in points.values()) / len(points)
    assert mean_distance(poses[300]) < mean_distance(poses[0]) * 0.7
    assert positions(poses[300])["fb0"] == pytest.approx(positions(poses[0])["fb0"], abs=1e-6)


def test_flocking_aligns_and_moves(experiments):
    poses, _ = experiments["flocking"]
    alignment = sum(polarization(poses[tick]) for tick in range(200, 301, 10)) / 11
    assert alignment > 0.7 and alignment > polarization(poses[0]) + 0.3
    displacement = sum(math.dist(poses[300][robot][:2], row[:2]) for robot, row in poses[0].items()) / 30
    assert displacement > 0.5


def test_mixed_flock_aligns_both_robot_types(experiments):
    poses, _ = experiments["mixed_flocking"]
    final = poses[300]
    assert polarization(final) > 0.7
    for kind in ("fb", "ep"):
        assert polarization({robot: row for robot, row in final.items() if robot.startswith(kind)}) > 0.7
