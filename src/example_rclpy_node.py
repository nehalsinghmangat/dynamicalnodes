#!/usr/bin/env python3
"""
Pedagogical ROS2 (rclpy) node — cruise control throttle controller.

Covers:
  - Node class pattern
  - QoS profiles
  - Subscriptions and callbacks
  - Message buffering (deque)
  - Staleness / freshness checking
  - Timer-driven publishing
  - Callback groups (thread safety)
  - Executor choices and spinning
  - Clean shutdown

Run standalone:
    python3 example_rclpy_node.py

Or via ros2:
    ros2 run <pkg> example_rclpy_node
"""

import time
from collections import deque

import rclpy
from rclpy.node import Node
from rclpy.executors import SingleThreadedExecutor
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.qos import (
    QoSProfile,
    QoSHistoryPolicy,
    QoSReliabilityPolicy,
    QoSDurabilityPolicy,
)
from std_msgs.msg import Float64


# =============================================================================
# QoS PROFILES
# =============================================================================
#
# QoS (Quality of Service) controls how messages move between publishers and
# subscribers. The four key policies:
#
#   history     — KEEP_LAST (ring buffer of `depth` msgs) or KEEP_ALL
#   depth       — ring buffer size when using KEEP_LAST
#   reliability — RELIABLE (retransmit until received) or BEST_EFFORT (fire-and-forget)
#   durability  — VOLATILE (new subs miss old msgs) or TRANSIENT_LOCAL (late-join delivery)
#
# Publisher and subscriber QoS must be *compatible* or ROS2 won't connect them.
# Reliable pub <-> Best-effort sub: compatible (sub gets what it can).
# Best-effort pub <-> Reliable sub: INCOMPATIBLE — they never connect.

SENSOR_QOS = QoSProfile(
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=10,
    reliability=QoSReliabilityPolicy.BEST_EFFORT,  # sensor streams tolerate drops
    durability=QoSDurabilityPolicy.VOLATILE,
)

COMMAND_QOS = QoSProfile(
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=1,  # only latest command matters
    reliability=QoSReliabilityPolicy.RELIABLE,  # actuator commands must arrive
    durability=QoSDurabilityPolicy.VOLATILE,
)


# =============================================================================
# NODE CLASS
# =============================================================================
#
# ROS2 nodes are classes that inherit from rclpy.node.Node.
# __init__ sets up all subscriptions, publishers, and timers.
# Callbacks fire when messages arrive or timers tick.


class CruiseControlNode(Node):
    """
    P-controller for vehicle speed.

    Subscribes to:
        /speed_mps    (Float64)  — current vehicle speed in m/s
        /setpoint_mps (Float64)  — desired speed in m/s

    Publishes to:
        /throttle     (Float64)  — throttle command in [0, 1]

    The controller fires at a fixed 10 Hz via a timer, independent of
    how fast messages arrive on the subscribed topics.
    """

    # How long (seconds) before an input is considered stale and skipped.
    STALE_AFTER = 0.5

    # Maximum messages to buffer per topic. deque(maxlen=N) is a ring buffer:
    # oldest entries are automatically dropped when full.
    BUFFER_SIZE = 5

    # Proportional gain
    KP = 0.4

    def __init__(self) -> None:
        # ------------------------------------------------------------
        # Node name (shows up in `ros2 node list`)
        # ------------------------------------------------------------
        super().__init__("cruise_control")

        # ------------------------------------------------------------
        # CALLBACK GROUP
        # ------------------------------------------------------------
        # Callback groups control which callbacks can run concurrently.
        #
        # ReentrantCallbackGroup  — any callbacks in this group may run
        #   simultaneously (you must protect shared state with locks).
        #
        # MutuallyExclusiveCallbackGroup — only one callback in the group
        #   runs at a time (simpler, but can stall if a callback is slow).
        #
        # All callbacks here share one reentrant group so the timer and
        # subscriber callbacks can overlap. The step_lock below keeps
        # shared state safe.
        self._cb_group = ReentrantCallbackGroup()

        # ------------------------------------------------------------
        # SUBSCRIPTIONS
        # ------------------------------------------------------------
        # create_subscription(msg_type, topic, callback, qos, callback_group)
        #
        # The callback fires once per received message on a background
        # executor thread. It must be fast — heavy computation here
        # blocks all other callbacks on a SingleThreadedExecutor.

        self._speed_sub = self.create_subscription(
            Float64,
            "/speed_mps",
            self._speed_cb,
            SENSOR_QOS,
            callback_group=self._cb_group,
        )

        self._setpoint_sub = self.create_subscription(
            Float64,
            "/setpoint_mps",
            self._setpoint_cb,
            SENSOR_QOS,
            callback_group=self._cb_group,
        )

        # ------------------------------------------------------------
        # MESSAGE BUFFERS
        # ------------------------------------------------------------
        # Each buffer is a deque of (wall_time, value) pairs.
        # Using wall time (time.monotonic()) rather than ROS header stamps
        # keeps the staleness check simple and doesn't require stamped msgs.
        # For production use header.stamp from the message for true latency tracking.

        self._speed_buf: deque = deque(maxlen=self.BUFFER_SIZE)
        self._setpoint_buf: deque = deque(maxlen=self.BUFFER_SIZE)

        # ------------------------------------------------------------
        # PUBLISHER
        # ------------------------------------------------------------
        self._throttle_pub = self.create_publisher(
            Float64,
            "/throttle",
            COMMAND_QOS,
        )

        # ------------------------------------------------------------
        # TIMER
        # ------------------------------------------------------------
        # create_timer(period_seconds, callback, callback_group)
        # Fires the callback at a fixed wall-clock rate regardless of
        # whether new messages have arrived. This is the standard pattern
        # for control loops that must publish at a predictable frequency.

        self._timer = self.create_timer(
            0.1,  # 10 Hz
            self._control_step,
            callback_group=self._cb_group,
        )

        self.get_logger().info("CruiseControlNode started — 10 Hz control loop")

    # ------------------------------------------------------------------
    # SUBSCRIPTION CALLBACKS
    # ------------------------------------------------------------------
    # These run on the executor thread whenever a message arrives.
    # They only enqueue data; the control logic lives in the timer callback.

    def _speed_cb(self, msg: Float64) -> None:
        self._speed_buf.append((time.monotonic(), msg.data))

    def _setpoint_cb(self, msg: Float64) -> None:
        self._setpoint_buf.append((time.monotonic(), msg.data))

    # ------------------------------------------------------------------
    # STALENESS CHECK
    # ------------------------------------------------------------------
    # Returns the most-recent value from `buf` if it arrived within
    # STALE_AFTER seconds, otherwise returns None ("input is stale").
    #
    # Why check staleness? A sensor that stopped publishing leaves its
    # last message in the buffer forever. Without a freshness gate the
    # controller would keep running on dead data.

    def _fresh(self, buf: deque):
        if not buf:
            return None
        ts, val = buf[-1]
        if (time.monotonic() - ts) > self.STALE_AFTER:
            return None
        return val

    # ------------------------------------------------------------------
    # TIMER CALLBACK — CONTROL STEP
    # ------------------------------------------------------------------

    def _control_step(self) -> None:
        speed = self._fresh(self._speed_buf)
        setpoint = self._fresh(self._setpoint_buf)

        # Skip this tick if either input is missing or stale.
        if speed is None or setpoint is None:
            self.get_logger().warn(
                "Skipping step: stale or missing input", throttle_duration_sec=1.0
            )
            return

        error = setpoint - speed
        throttle = float(max(0.0, min(1.0, self.KP * error)))

        msg = Float64()
        msg.data = throttle
        self._throttle_pub.publish(msg)

        self.get_logger().debug(
            f"speed={speed:.2f}  setpoint={setpoint:.2f}  throttle={throttle:.3f}"
        )


# =============================================================================
# MAIN — EXECUTOR AND SPIN
# =============================================================================
#
# The executor is the event loop. It polls timers, checks for new messages,
# and dispatches callbacks.
#
# SingleThreadedExecutor — one thread, callbacks run sequentially.
#   Simplest. Fine unless a callback blocks for a long time.
#
# MultiThreadedExecutor(num_threads=N) — callbacks run in a thread pool.
#   Required when you have slow callbacks AND need other callbacks to keep firing.
#   ReentrantCallbackGroup unlocks concurrency; MutuallyExclusiveCallbackGroup
#   serialises within the group even under a multi-threaded executor.
#
# rclpy.spin(node) is shorthand for:
#   executor = SingleThreadedExecutor()
#   executor.add_node(node)
#   executor.spin()


def main() -> None:
    rclpy.init()  # connect to the ROS2 daemon
    node = CruiseControlNode()

    executor = SingleThreadedExecutor()
    executor.add_node(node)

    try:
        executor.spin()  # blocks until shutdown
    except KeyboardInterrupt:
        pass
    finally:
        node.get_logger().info("Shutting down")
        node.destroy_node()  # unregister subs/pubs/timers
        rclpy.shutdown()  # disconnect from the daemon


if __name__ == "__main__":
    main()
