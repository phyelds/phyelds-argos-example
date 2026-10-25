"""The sensors and outputs that phyelds-argos gives every robot, named once.

Moving a robot is the ``velocity`` actuator of ``phyelds.libraries.device``, in m/s.
"""
from phyelds.libraries.device import Actuator, Sensor

source: Sensor[bool] = Sensor("source")
"""Whether the robot is the one the experiment names in ``source``."""

heading: Sensor[tuple[float, float, float]] = Sensor("heading")
"""Where the robot faces: a unit vector in the global compass frame."""

obstacle: Sensor[tuple[float, float, float]] = Sensor("obstacle")
"""Away from what the proximity sensors see, in the compass frame; absent without them."""

led: Actuator[tuple[int, int, int]] = Actuator("led")
"""The colour of the robot's LEDs, as integer RGB channels in 0–255."""

label: Actuator[str] = Actuator("label")
"""The text the GUI writes above the robot."""
