---
name: wrap-in-rosnode
description: Wrap dynamicalnodes DynamicalSystem blocks in ROSNode objects (subs, pubs, topics, message types, converters, state_name) and re-run the simulation for-loop on ROS message types to verify the translation. Use when the user wants to create ROSNode objects, choose topics/msg types, wire blocks together over topics, or test that the ROS version behaves like the Python loop before generating rclpy files.
---

# Wrap DynamicalSystems in ROSNodes and test the loop

Prerequisite: a working Python loop (see `simulate-with-dynamicalsystem`). Background: tutorial sections "The `ROSNode` Class (III-C)" and "Testing Data Translation" in `docs/source/tutorials/0_cruise_control/cruise_control_with_dynamicalnodes.ipynb`; API in `docs/source/api/rosnode.rst`; node semantics in `CLAUDE.md`.

`ROSNode.step()` is pure Python/NumPy: no running ROS needed. You only need the ROS message *classes* and the converters importable (a ROS2 install, sourced).

## Steps

1. **List every signal in the diagram as a topic.** One topic per arrow (`/rk`, `/uk`, `/yk`, `/xhatk`: the signal's name). Pick a message type per topic (`std_msgs/Float64` for scalars; `Float64MultiArray`, `Vector3`, `Imu`, `Odometry`, ... otherwise).
2. **Pick converters** for each topic: `ros2py_<type>` for subscriptions, `py2ros_<type>` for publications, from `dynamicalnodes.ros2py_py2ros`. If the pair doesn't exist, use the `write-ros-converters` skill.
3. **Build one `ROSNode` per block**:
   ```python
   ROSNode(dynamical_system=ds,
           state_name="ck",                       # f's state parameter, if f exists
           subs=[{"topic": "/rk", "msg_type": Float64,
                  "arg": "rk", "ros2py": ros2py_float64}],
           pubs=[{"topic": "/uk", "msg_type": Float64, "py2ros": py2ros_float64}])
   ```
   - `arg` must equal the **exact parameter name** in `f`/`h` that receives that topic.
   - `state_name` must equal the **exact name of the state parameter** of `f` (`ck`, `xk`, `ok`). Omit it for stateless `(*, h)` blocks.
   - Subscription extras: `buffer_size` (default 1), `use_msg_timestamp`. Publication extra: `key`, needed when `h` returns a dict and there are several publishers.
   - Deployment settings (`node_name`, `sync_mode`, `timer_hz`, `stale_after`) do **not** go here; they go to `write_ROSNode_to_rclpy` (skill `deploy-rosnodes-to-rclpy`).
4. **Seed states.** The tutorial sets `node._state = ...` (the same initial values as the Python loop). Feedback inputs that don't exist yet at iteration 0 are initial *messages*, e.g. `yk_ros = Float64(data=0.0)`.
5. **Re-run the same loop**, replacing `block.step(...)` by `node.step(...)`: inputs are the messages returned by the upstream nodes, parameters (`dt`, gains, ...) are still passed as kwargs. A node with one publisher returns its message; with several it returns `{topic: msg}`; with none it returns the raw `h` output.
6. **Compare with the Python loop.** Seed the noise (`np.random.seed(0)`) before each loop: histories should be identical (the Python and ROSNode loops of the cruise-control example agree to 0.0). Read `msg.data` for plotting (matplotlib can't plot ROS messages), or call the `ros2py_*` converter.

## What conversion does

- Incoming messages (or plain arrays) are converted with `ros2py` and cast to float arrays. `None` inputs are skipped, so an optional `uk=None` still works.
- The block's **state is not converted**: tuples and arrays stay Python objects inside the node.
- Outgoing values are `np.asarray(val, float).ravel()` before `py2ros`, so a `py2ros_*` function always receives a flat float array.

## Common mistakes

- `arg`/`state_name` don't match the function signatures: the input is dropped silently or the state is never injected.
- Wrong or missing converter for the message type (shape/order mismatch). Check one round trip by hand.
- Forgetting initial feedback messages, or expecting scalar `float` back from a filter whose converter returns an array.
- Putting `sync_mode`/`timer_hz` in the constructor: they belong to `write_ROSNode_to_rclpy`.
- Duplicated topic names, or one topic with two publishers, in the graph.
- Treating the ROSNode loop as a timing test: it is not. It only validates translation and wiring; timing behavior is decided at deployment.

Next: `deploy-rosnodes-to-rclpy`.
