#!/usr/bin/env python3
"""
Launch all four cruise-control nodes as separate processes.

Topic graph:
    reference  →  /rk    →  controller
    controller →  /uk    →  plant, kalman
    plant      →  /yk    →  kalman
    kalman     →  /xhatk →  controller

Startup ordering:
    Nodes may start in any order. The controller's initial_inputs={"xhatk": 0.0}
    provides a cold-start value for /xhatk so it does not stall waiting for the
    Kalman filter to produce its first estimate.

Run:
    ros2 launch ros_nodes/cruise_control.launch.py

Tune PID gains at runtime (no restart required):
    ros2 param set /controller KP 600.0
    ros2 param set /controller KI 25.0
    ros2 param set /controller KD 15.0

Inspect:
    ros2 topic echo /uk
    rqt_graph
"""

import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, TimerAction


def generate_launch_description() -> LaunchDescription:
    here = os.path.dirname(os.path.abspath(__file__))

    def py_node(script: str) -> ExecuteProcess:
        return ExecuteProcess(
            cmd=["python3", os.path.join(here, script)],
            output="screen",
        )

    return LaunchDescription(
        [
            py_node("reference_node.py"),
            py_node("controller_node.py"),
            py_node("plant_node.py"),
            py_node("kalman_node.py"),
            # Delay rqt_graph so all nodes have registered before it opens.
            TimerAction(
                period=2.0,
                actions=[ExecuteProcess(cmd=["rqt_graph"])],
            ),
        ]
    )
