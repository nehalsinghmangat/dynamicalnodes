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
   - Encapsulates an evolution function `f(x_k, u_k, theta) → x_{k+1}` and a measurement function `h(x_k, u_k, theta) → y_k`, either of which may be `None`
   - `eval(**kwargs)` returns `(x_{k+1}, y_k)`, substituting `None` for whichever of `f`/`h` is unset (`(f, *)`, `(*, h)`, or `(f, h)`); raises `ValueError` if both are unset
   - `_bind_and_call()` dispatches only the kwargs each function declares in its signature

2. **`rosnode.py`** — `ROSNode` class
   - Wraps a `DynamicalSystem` for both notebook simulation (`eval()`) and ROS2 deployment (`write_ROSNode_to_rclpy()`)
   - `subs`: list of dicts, each with `topic`, `msg_type`, `arg` (kwarg name passed to `eval()`), `ros2py` (converter), and optional `stale_after`/`buffer_size`/`use_msg_timestamp`
   - `pubs`: list of dicts, each with `topic`, `msg_type`, `py2ros` (converter), and optional `key` (required when there are multiple publishers)
   - Staleness policy: per-subscription `stale_after` (seconds); a stale/missing input is dropped (passed as `None`), not reused from an old value
   - No direct dependency on `rclpy` at import time — `subs`/`pubs` use duck-typing (`__slots__`/`_fields_and_field_types`) to detect ROS messages, and `write_ROSNode_to_rclpy()` only *emits* rclpy imports into the generated file

3. **`ros2py_py2ros.py`** — message conversion functions
   - Individually named `ros2py_<type>`/`py2ros_<type>` function pairs (no registry dict)
   - Covers geometry_msgs, nav_msgs, sensor_msgs, std_msgs, turtlesim
   - Imports `rclpy` and the ROS `*_msgs` packages at module level — requires a live ROS2 installation

4. **`__init__.py`** — public API
   - Eager: `DynamicalSystem`, `ROSNode` — neither has a module-level ROS2 dependency
   - Lazy (ROS2-optional, via `__getattr__`): `ros2py_py2ros`

### Key Design Patterns

**Composability**: Every control component is a `DynamicalSystem`. The `_bind_and_call()` mechanism binds kwargs by name, so components with different signatures compose without rigid interfaces.

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

### DynamicalSystem.eval()

`eval(**kwargs)` lexically binds keyword arguments by name to whichever of `f` and/or `h` declare them in their signature, then calls the appropriate function(s):
- `(*, h)` — stateless: returns `(None, y_k)`
- `(f, *)` — no output: returns `(x_{k+1}, None)`
- `(f, h)` — both: calls `f` and `h` with the **same original kwargs**, returning `(x_{k+1}, y_k)`, where `h(x_k, ...)` computes the observation `y_k` from the **pre-update** state
- Raises `ValueError` if neither `f` nor `h` is defined

So when both `f` and `h` are defined, the returned observation is one step behind the returned state. In simulation loops,
access the updated state directly (e.g., `x_next, _ = block.eval(...)`) when you need the post-update value.

### ROSNode

- `subs` entries: dicts with `topic`, `msg_type`, `arg`, `ros2py`, and optional `stale_after`/`buffer_size`/`use_msg_timestamp`
- `pubs` entries: dicts with `topic`, `msg_type`, `py2ros`, and optional `key` (required when there's more than one publisher)
- Staleness is per-subscription (`stale_after` seconds); a stale or missing input is silently dropped (`None`), not reused from an old value
- `eval()` never touches `rclpy` — it's pure Python/NumPy, so no ROS2 installation is needed for simulation
- `rclpy.init()`/node construction only happens in the file generated by `write_ROSNode_to_rclpy()`, in its `main()` entry point

### Message Conversion

`ros2py_py2ros.py` provides individually named converter functions (e.g. `ros2py_float64`/`py2ros_float64`, `ros2py_imu`/`py2ros_imu`) — there is no registry dict. To support a new ROS message type, add a `ros2py_<type>`/`py2ros_<type>` function pair and pass them explicitly via the `"ros2py"`/`"py2ros"` keys in a `ROSNode`'s `subs`/`pubs` dicts.

## Project Structure

```
src/dynamicalnodes/
├── __init__.py              # Public API (DynamicalSystem, ROSNode eager; ros2py_py2ros lazy)
├── dynamical_system.py      # Core DynamicalSystem abstraction
├── rosnode.py               # ROS2 node wrapper
└── ros2py_py2ros.py         # Message conversion functions

docs/
├── source/
│   ├── conf.py              # Sphinx config (myst_nb, autodoc, napoleon, rtd theme)
│   ├── index.rst            # Landing page
│   ├── installation.rst
│   ├── license.rst
│   ├── api/                 # API reference (.rst per module)
│   │   ├── dynamical_system.rst
│   │   └── rosnode.rst
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
