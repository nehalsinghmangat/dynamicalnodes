---
name: deploy-rosnodes-to-rclpy
description: Generate standalone rclpy node files from dynamicalnodes ROSNode objects with write_ROSNode_to_rclpy, choose sync_mode, timer_hz, stale_after, initial_inputs, static and dynamic params, convert simulation dt to node rates, run the nodes, tune parameters live, and debug a node that does nothing or behaves differently from the Python simulation. Use for deploying to ROS2, launch files, rqt_graph, ros2 param, or timing/staleness questions.
---

# Generate, run and debug rclpy nodes

Prerequisite: `ROSNode` objects whose `.step()` loop matches the Python loop (see `wrap-in-rosnode`). Background: tutorial sections "Generating `rclpy` files", "Sim Time to Node Time", "Running the Nodes" and "Generating the ROS Graph (IV-E)" in `docs/source/tutorials/0_cruise_control/cruise_control_with_dynamicalnodes.ipynb`; full semantics in `CLAUDE.md` ("Generated-node semantics"); API in `docs/source/api/rosnode.rst`.

## Requirements (check first)

`write_ROSNode_to_rclpy` inlines the source of `f`, `h` and any non-package converters, so:

- they must be **named functions** (no lambdas; `ValueError` otherwise);
- their **source must be retrievable**: defined in a file or notebook cell, not via `exec`, not C extensions (`OSError`);
- they must be **self-contained**: helper functions go in `deps=[...]`; imports used inside must be available in the generated file;
- every parameter without a default must be supplied via `static_params` or `dynamic_params` (or by a subscription).

## Steps

1. **Convert sim `dt` into a rate.** Only the node that has **no subscriptions** (the reference generator) needs `timer_hz = 1/dt`; every other node is callback-driven and inherits that rate. Keep the model's `dt` as a static parameter equal to the real period, and **recompute any `dt`-dependent matrices** (`Fk`, `Bk`, `Qk`, ...) for `dt_ros`. A Δt that doesn't match the message period makes the physics wrong.
2. **Write one file per node**:
   ```python
   ref_node.write_ROSNode_to_rclpy("ros_nodes/reference_node.py", node_name="reference",
       timer_hz=1 / dt, static_params={"A": 30.0, "omega": np.pi / 60})
   pid_node.write_ROSNode_to_rclpy("ros_nodes/pid_node.py", node_name="pid",
       sync_mode="all", stale_after={"rk": 2 * dt, "yk": 2 * dt},
       initial_state=(0.0, 0.0), initial_inputs={"yk": 0.0},
       static_params={"dt": dt}, dynamic_params={"KP": 500.0, "KI": 30.0, "KD": 10.0})
   car_node.write_ROSNode_to_rclpy("ros_nodes/car_node.py", node_name="car",
       initial_state=0.0, static_params={"dt": dt, "sigma": 0.5})
   ```
3. **Pick `sync_mode`** (required with more than one subscription):
   - `"any"`: step on every message; an absent input arrives as `None`. Use for estimators that can predict or update independently. The block must tolerate `None` (optional args).
   - `"all"`: step only when **every** subscription holds a fresh message. Use for controllers that need all inputs together.
4. **Set `stale_after`** (seconds, per `arg`): a small multiple of the period (1.5–2×), tight enough to reject old data, loose enough for jitter.
5. **Break startup deadlocks with `initial_inputs`**: a loop (PID needs the estimate, the filter needs the control) never starts unless one node has a cold-start value. It is used only until the *first message ever* arrives; after that it is never reused.
6. **Params**: `static_params` are baked in; `dynamic_params` become ROS2 parameters, tunable live: `ros2 param set /pid KP 600.0`.
7. **Run**, with ROS2 sourced:
   ```bash
   python3 ros_nodes/reference_node.py &  python3 ros_nodes/pid_node.py &  python3 ros_nodes/car_node.py &
   rqt_graph              # topology; PlotJuggler / `ros2 topic echo` for signals
   ```
   Startup order doesn't matter. Stop with Ctrl-C or `pkill -f ros_nodes/`. The tutorial also writes a launch file (`ros_nodes/cruise_control.launch.py`) that starts every node and `rqt_graph`.

A three-node graph built exactly like the example above was verified: `/rk`, `/uk` and `/yk` all publish.

## Semantics worth remembering

- Inputs are **consumed** when used: an unchanged input arrives as `None` on the next step. A new `/uk` never re-processes an old `/yk`.
- Under `"all"`, a constant reference published **once** drives exactly one step. Publish it periodically.
- `tk` (if declared) is wall-clock seconds since node start.
- Python and ROS runs are not sample-identical: wall-clock timing and message arrival order differ, and noise draws differ unless seeded.
- A feedback signal reaches its consumer one step later in ROS than in the loop (the value published at step `k` is used at step `k+1`).

## Debugging checklist

1. **Node does nothing**: `sync_mode="all"` with an input that is stale or published once; no subscriptions and no `timer_hz` (`ValueError` at generation); a startup loop with no `initial_inputs`.
2. **`ValueError` at generation**: lambda, missing `sync_mode` with several subs, non-positive `timer_hz`. **`OSError`**: source not retrievable. Move the function to a file or add `deps`.
3. **Wrong numbers vs the simulation**: `dt` mismatch between model and timer; matrices not recomputed for `dt_ros`; stale `static_params`; unseeded noise.
4. **Filter drifts**: with `sync_mode="any"` the node may see `uk` before `yk`, so it predicts before updating with a measurement of the earlier state. Consider `sync_mode="all"` or accept the approximation.
5. **Check the wiring** with `ros2 node list`, `ros2 topic list`, `ros2 topic hz`; `ros2 topic echo` can need a few seconds to discover a fresh domain.
6. **Python/ROS version**: ROS2 packages (`rclpy`, `std_msgs`, ...) are system packages. In a fresh virtualenv you may also need `pyyaml` and `typeguard`. Generated nodes exit cleanly on Ctrl-C and SIGTERM as of dynamicalnodes 0.2.1.

Regenerate the files after any change to `f`, `h`, converters or parameters; the generated files are artifacts, not sources.
