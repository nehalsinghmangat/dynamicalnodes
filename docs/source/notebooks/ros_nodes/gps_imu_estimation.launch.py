#!/usr/bin/env python3
"""
Launch all four GPS-IMU state estimation nodes as separate processes.

Topic graph:
    gps          →  /gps      →  kf_estimator, ann_estimator
    imu          →  /imu      →  kf_estimator, ann_estimator
    kf_estimator →  /x_est_kf
    ann_estimator→  /x_est_ann

Startup ordering:
    Nodes may start in any order. kf_estimator handles a missing GPS gracefully
    (predict-only until the first /gps message arrives). ann_estimator waits
    silently until both /gps and /imu are fresh before publishing.

Run:
    ros2 launch ros_nodes/gps_imu_estimation.launch.py

Observe sync_mode difference at runtime:
    ros2 topic hz /x_est_kf    # ~101 Hz  (sync_mode="any": fires on every IMU msg)
    ros2 topic hz /x_est_ann   #   ~1 Hz  (sync_mode="all": GPS is the bottleneck)

Kill GPS to see KF keep predicting while ANN goes silent:
    pkill -f gps_node.py       # ANN stops; KF continues from IMU alone

Inspect:
    ros2 topic echo /x_est_kf
    ros2 topic echo /x_est_ann
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
            py_node("gps_node.py"),
            py_node("imu_node.py"),
            py_node("kf_estimator_node.py"),
            py_node("ann_estimator_node.py"),
            # Delay rqt_graph so all nodes have registered before it opens.
            TimerAction(
                period=2.0,
                actions=[ExecuteProcess(cmd=["rqt_graph"])],
            ),
        ]
    )
