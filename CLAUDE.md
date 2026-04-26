# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**dynamicalnodes** is a Python development framework bridging theoretical control systems and hardware implementation for robotics. It follows a four-step pipeline: Theory → Python → ROS2 → Hardware.

The framework enables users to:
1. Model control systems as composable `DynamicalSystem` blocks
2. Implement estimators (e.g., Kalman filters) and controllers as pure Python functions
3. Wrap these systems in ROS2 nodes for simulation and hardware deployment
4. Deploy seamlessly from Python to physical robots

## Core Architecture

### Source Files

All source lives under `src/dynamicalnodes/` (flat layout, no subdirectories):

1. **`dynamical_system.py`** — `DynamicalSystem` class
   - Encapsulates state transition `f(x_k, ...) → x_{k+1}` and observation `h(x_k, ...) → y_k`
   - `step(**kwargs)` returns `(x_{k+1}, y_k)` for stateful systems, `y_k` for stateless
   - `_smart_call()` dispatches only the kwargs each function declares in its signature

2. **`rosnode.py`** — `ROSNode` class
   - Wraps a Python callback as a ROS2 node
   - Subscriptions: `(topic, msg_type, arg_name)` tuples; messages auto-converted via `ROS2PY_DEFAULT`
   - Publications: `(return_key, msg_type, topic)` tuples; arrays auto-converted via `PY2ROS_DEFAULT`
   - Staleness policy: `_arg_stale_after` dict — drops stale inputs rather than using old values
   - Only ROS-dependent file; import fails gracefully without ROS2

3. **`rostools.py`** — ROS2 notebook utilities
   - `reset_ros()`, `list_nodes()`, `list_topics()`, `list_services()`, `node_info()`, `topic_info()`
   - `echo(topic, msg_type, n, timeout)` — capture messages from a live topic
   - `rqt_graph()`, `rqt(plugin)`, `rviz2(config)` — background GUI launchers

4. **`ros2py_py2ros.py`** — message conversion registries
   - `ROS2PY_DEFAULT`: ROS msg → NumPy array
   - `PY2ROS_DEFAULT`: NumPy array → ROS msg
   - Covers geometry_msgs, nav_msgs, sensor_msgs, std_msgs, turtlesim

5. **`__init__.py`** — public API
   - Eager: `DynamicalSystem`, `rostools`
   - Lazy (ROS2-optional): `ROSNode`, `reset_ros`

### Key Design Patterns

**Composability**: Every control component is a `DynamicalSystem`. The `_smart_call()` mechanism binds kwargs by name, so components with different signatures compose without rigid interfaces.

**Event-driven ROSNode**: No fixed-rate publishing. The node fires its callback whenever a fresh message arrives on any subscribed topic; stale inputs are dropped.

## Development Commands

### Testing
```bash
pytest                                         # all doctests
pytest --doctest-modules src/dynamicalnodes/dynamical_system.py  # one file
pytest -v
```

### Documentation
```bash
cd docs
make html          # build to docs/build/html/
make clean         # wipe build artifacts
```

Documentation deploys to GitHub Pages via `.github/workflows/docs.yml` on push to `main`.

### Code Quality
```bash
black src/
isort src/
mypy src/
flake8 src/
```

### Building and Publishing
```bash
python -m build
twine check dist/*
twine upload dist/*   # requires credentials; also automated via GitHub Actions on release
```

## Important Implementation Details

### DynamicalSystem.step()

`step(**kwargs)` calls both `f` and `h` with the **same original kwargs**:
- `f(x_k, ...)` computes next state `x_{k+1}`
- `h(x_k, ...)` computes observation `y_k` from the **pre-update** state

So the returned observation is one step behind the returned state. In simulation loops,
access the updated state directly (e.g., `x_next, _ = block.step(...)`) when you need the post-update value.

### ROSNode

- Subscription tuple: `(topic_name, msg_type, arg_name)` — 3 elements
- Publication tuple: `(return_key, msg_type, topic_name)` — 3 elements
- `_arg_stale_after: Dict[str, Optional[float]]` — seconds after which an input is considered stale
- Stale inputs are silently dropped; callback only fires when `sync_mode` is satisfied
- Always call `rclpy.init()` before creating nodes (handled automatically)

### Message Conversion

To add support for a new ROS message type, add entries to both `ROS2PY_DEFAULT` and `PY2ROS_DEFAULT` in `ros2py_py2ros.py`.

## Project Structure

```
src/dynamicalnodes/
├── __init__.py              # Public API (DynamicalSystem, ROSNode, rostools)
├── dynamical_system.py      # Core DynamicalSystem abstraction
├── rosnode.py               # ROS2 node wrapper
├── rostools.py              # ROS2 notebook utilities
└── ros2py_py2ros.py         # Message conversion registries

docs/
├── source/
│   ├── conf.py              # Sphinx config (myst_nb, autodoc, napoleon, rtd theme)
│   ├── index.rst            # Landing page
│   ├── installation.rst
│   ├── license.rst
│   ├── api/                 # API reference (.rst per module)
│   │   ├── dynamical_system.rst
│   │   ├── rosnode.rst
│   │   └── rostools.rst
│   ├── notebooks/
│   │   └── cruise_control.ipynb   # Main demo: Car+PID+KF, Drone+LQR+UKF
│   └── _static/css/custom.css
├── Makefile
└── build/html/              # Generated output (not committed)

.github/workflows/
├── docs.yml                 # Deploy docs to GitHub Pages on push to main
└── publish.yml              # Publish to PyPI on release
```

## Python Version

Requires Python >=3.12 (specified in pyproject.toml)

## Dependencies

Core: `numpy>=1.24`
Dev: `pytest`, `pytest-doctestplus`, `flake8`, `black`, `isort`, `mypy`, `build`, `twine`
Docs: `sphinx`, `sphinx-rtd-theme`, `myst_nb`, `sphinx-autodoc-typehints`, `matplotlib`, `scipy`, `jupyter`
ROS2 (system packages, not on PyPI): `rclpy`, `geometry_msgs`, `sensor_msgs`, `nav_msgs`, `std_msgs`, `turtlesim`

## Testing Philosophy

The project uses doctests over unit tests. When adding functionality:
- Include doctest examples in docstrings showing typical usage
- Use `NORMALIZE_WHITESPACE` and `ELLIPSIS` options (configured globally in pyproject.toml)
- Ensure examples are self-contained and runnable without ROS2
