---
name: write-ros-converters
description: Write a ros2py_<type> / py2ros_<type> message conversion function pair for a ROS message type that dynamicalnodes doesn't already cover, and test it. Use when the user needs to subscribe to or publish a message type with no converter in dynamicalnodes.ros2py_py2ros, or asks how translation between ROS messages and Python/NumPy works.
---

# Write a ROS ↔ Python converter pair

Converters are plain functions, passed explicitly to a `ROSNode` via the `"ros2py"` / `"py2ros"` keys of `subs` / `pubs`. There is no registry. Background: tutorial section "Testing Data Translation" in `docs/source/tutorials/0_cruise_control/cruise_control_with_dynamicalnodes.ipynb`; existing converters in `src/dynamicalnodes/ros2py_py2ros.py`; API page `docs/source/api/ros2py_py2ros.rst`.

## First, look for an existing pair

`dynamicalnodes.ros2py_py2ros` already covers `std_msgs` (Float64, Int32, multiarrays), `geometry_msgs` (Vector3, Quaternion, Pose, Twist, Wrench, Transform, Accel and their `Stamped`/covariance variants), `sensor_msgs` (Imu, NavSatFix, JointState, LaserScan, Image, CompressedImage), `nav_msgs` (Odometry, Path) and `turtlesim`. Search the module for `def ros2py_` before writing a new one.

## Contract

- `ros2py(msg) -> float | np.ndarray | dict`: the value the block's `f`/`h` receives for this input. Keep it numeric and flat unless the block needs structure.
- `py2ros(arr) -> msg`: `ROSNode` always passes `np.asarray(value, float).ravel()`, a **flat float array**. Reshape inside the function if you need structure.
- Document the array layout in the docstring (field order, units, length). Stamped messages in this package encode time as the first element, in seconds (`ros2py_time` / `py2ros_time`).
- Validate length in `py2ros` and raise `ValueError` on a mismatch (see `py2ros_pose_stamped`).
- Optional extras (like `frame_id`) are keyword-only arguments with defaults. `ROSNode` never passes them, so the default is used. To fix a different value, define a small *named* wrapper that sets it; a `functools.partial` is not a named function and cannot be deployed.

## Template

```python
import numpy as np
from geometry_msgs.msg import Point

def ros2py_point(msg: Point) -> np.ndarray:
    """Point -> [x, y, z]."""
    return np.array([msg.x, msg.y, msg.z], dtype=float)

def py2ros_point(arr) -> Point:
    """[x, y, z] -> Point."""
    flat = np.asarray(arr, dtype=float).ravel()
    if flat.size != 3:
        raise ValueError(f"py2ros_point expected length 3, got {flat.size}")
    msg = Point()
    msg.x, msg.y, msg.z = map(float, flat)
    return msg
```

Use it: `{"topic": "/goal", "msg_type": Point, "arg": "goal", "ros2py": ros2py_point}`.

## Test before using

```python
msg = Point(x=1.0, y=2.0, z=3.0)
assert np.allclose(ros2py_point(py2ros_point(ros2py_point(msg))), [1, 2, 3])
```

Then run it through a `ROSNode.step()` (see `wrap-in-rosnode`).

## Deployment constraints

`write_ROSNode_to_rclpy` handles converters like this: functions from `dynamicalnodes.ros2py_py2ros` (or any importable module) are **imported by name**; functions defined in a notebook or script are **inlined from their source**. So an inlined converter must be a named function, define no lambdas, and be self-contained: import any message class it uses (other than the topic's `msg_type`) *inside* the function body.

## Contributing the pair to the package

1. Add the pair to `src/dynamicalnodes/ros2py_py2ros.py` under a section comment, with the message import at the top and a docstring giving the array layout. Keep the naming `ros2py_<type>` / `py2ros_<type>`.
2. The API page uses `automodule`, so no `.rst` edit is needed, but update the coverage list in `CLAUDE.md` if you add a new message package.
3. Don't add a registry or a dict of converters.

## Common mistakes

- Assuming `py2ros` receives a scalar or nested structure: it receives a flat float array.
- Returning an array where `f`/`h` expect a float (or the opposite).
- Lambdas as converters in anything you will deploy.
- Reusing one message object across calls: build a fresh message each time.
