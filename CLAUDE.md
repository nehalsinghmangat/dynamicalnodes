# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**dynamicalnodes** is a Python development framework bridging theoretical control systems and hardware implementation for robotics. It follows a four-step pipeline: Theory → Software → Simulation → Hardware.

The framework enables users to:
1. Model control systems as composable dynamical systems
2. Implement estimators (e.g., Kalman filters) and controllers as pure Python functions
3. Wrap these systems in ROS2 nodes for simulation and hardware deployment
4. Deploy seamlessly from software to Gazebo simulation to physical robots

## Core Architecture

### Three Main Components

1. **DynamicalSystem** (`src/dynamicalnodes/dynamical_system.py`)
   - Core abstraction for modeling any control system component
   - Encapsulates state evolution (`f`) and observation (`h`) functions
   - Uses `_smart_call()` for flexible parameter binding from a shared parameter dictionary
   - The `step()` method executes one iteration: state update → observation
   - Components can be composed by chaining outputs to inputs

2. **ROSNode** (`src/dynamicalnodes/ros_node.py`)
   - Wraps arbitrary Python callbacks as ROS2 nodes
   - Maps ROS topics to Python function arguments and return values
   - Handles message conversion via `ROS2PY_DEFAULT` and `PY2ROS_DEFAULT` registries
   - Manages threading, executors, staleness policies, and node lifecycle
   - **Critical**: The node is created separately from spinning; use `create_node()` before `start()`

3. **Utilities** (`src/dynamicalnodes/utilities/`)
   - `estimators/kf.py`: Kalman filter implementation as DynamicalSystem-compatible functions
   - `ros2py_py2ros.py`: Bidirectional converters between ROS messages and NumPy arrays
   - `gazebo.py`: Gazebo simulation launcher for Jupyter notebooks (start_gazebo/stop_gazebo)
   - Converter registries (`ROS2PY_DEFAULT`, `PY2ROS_DEFAULT`) for automatic message handling
   - **ROS2 Optional**: `ros2py_py2ros` uses lazy imports - only fails if actually used without ROS2 installed

### Key Design Patterns

**Composability**: All control components (plants, observers, controllers, setpoint generators) are modeled as DynamicalSystems with `f` and `h` functions. They share a common parameter dictionary, allowing flexible composition.

**Message Conversion**: ROS2 messages are automatically converted to/from NumPy arrays using registered converter functions. To add support for a new message type, add entries to both `ROS2PY_DEFAULT` and `PY2ROS_DEFAULT` in `ros2py_py2ros.py`.

**Smart Parameter Binding**: The `_smart_call()` method inspects function signatures and binds available parameters from a shared dictionary, enabling flexible function composition without rigid interfaces.

## Development Commands

### Environment Setup
```bash
# Activate virtual environment (if not already active)
source .venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Install with documentation dependencies
pip install -e ".[docs]"
```

### Testing
```bash
# Run all doctests (configured in pytest.ini and pyproject.toml)
pytest

# Run specific doctest in a file
pytest --doctest-modules src/dynamicalnodes/dynamical_system.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=dynamicalnodes --cov-report=html
```

The project uses doctests extensively. All `.py` files are tested for embedded doctests via the `--doctest-glob="*.py"` configuration.

### Documentation
```bash
# Build Sphinx documentation (requires venv activation)
source .venv/bin/activate
cd docs
make html

# View documentation (built to docs/build/html/)
# Open docs/build/html/index.html in browser

# Clean documentation build
make clean

# Regenerate bibliography metadata after updating references.bib
python3 docs/generate_bib_metadata.py
```

Documentation is hosted on ReadTheDocs at https://dynamicalnodes.readthedocs.io

**Bibliography System**: The Algorithm Library shows clickable colored circles linking to implementation notebooks:
- Blue circle: `impl_dynamicalnodes` field in `references.bib`
- Green circle: `impl_turtlebot` field
- Yellow circle: `impl_crazyflie` field

Workflow to add new implementation:
1. Create notebook in `docs/source/notebooks/`
2. Update `docs/source/references.bib` with path (relative to `docs/source/`)
3. Run `python3 docs/generate_bib_metadata.py` to regenerate metadata
4. Run `cd docs && make html` to rebuild documentation

### Code Quality
```bash
# Format code with black
black src/

# Sort imports with isort
isort src/

# Type checking with mypy
mypy src/

# Linting with flake8
flake8 src/

# Linting with pylint
pylint src/dynamicalnodes/
```

### Building and Publishing
```bash
# Build package
python -m build

# Check distribution
twine check dist/*

# Upload to PyPI (requires credentials)
twine upload dist/*
```

Note: Publishing is automated via GitHub Actions on release.

## Important Implementation Details

### Working with DynamicalSystem

When creating or modifying DynamicalSystem instances:
- If `f` is provided, `state_name` must also be provided (raises ValueError otherwise)
- The `step()` method updates state via `f`, stores it in `param_dict[state_name]`, then calls `h`
- Use `return_state=True` in `step()` to get both the new state and observation as a tuple
- The `h` function defaults to identity if not provided

### Working with ROSNode

When creating ROSNode wrappers:
- The callback receives `tk` (time in seconds) as first argument, followed by subscribed topics as kwargs
- The callback must return a dictionary mapping return keys to NumPy arrays
- Subscription format: `(topic_name, msg_type, arg_name)` - the msg_type must exist in `ROS2PY_DEFAULT`
- Publication format: `(return_key, msg_type, topic_name)` - the msg_type must exist in `PY2ROS_DEFAULT`
- Staleness configuration: `{"arg_name": {"after": 0.5, "policy": "zero"|"hold"|"drop"}}`
- Always call `rclpy.init()` before creating nodes (handled automatically in `create_node()` if needed)

### Working with Estimators

The Kalman filter (`utilities/estimators/kf.py`):
- `KF.f()` performs predict-update cycle, returns `(x_updated, P_updated)`
- `KF.h()` extracts state estimate from the tuple `(x, P) -> x`
- Takes functions `f`, `F`, `Q`, `h`, `H`, `R` as parameters (dynamics, Jacobians, covariances)
- Each function receives its own parameter dictionary (`f_params`, `F_params`, etc.)
- Uses ridge regularization and pseudo-inverse fallback for numerical stability

### Working with Gazebo Simulations

The Gazebo launcher (`utilities/gazebo.py`):
- `start_gazebo(robot, world, headless, x_pose, y_pose, z_pose, yaw)` launches Gazebo simulation
- Returns `GazeboProcess` object for lifecycle management
- `stop_gazebo(gz)` cleanly shuts down simulation
- Supports `robot='turtlebot3'` and `robot='crazyflie'`
- Use `headless=True` for faster simulation without GUI
- Designed for Jupyter notebook integration (see `docs/source/notebooks/`)

## Project Structure

```
src/dynamicalnodes/
├── __init__.py              # Exports DynamicalSystem, ROSNode, utilities
├── dynamical_system.py      # Core DynamicalSystem abstraction
├── ros_node.py              # ROS2 node wrapper
└── utilities/
    ├── __init__.py          # Lazy imports for ROS2 dependencies
    ├── estimators/
    │   ├── __init__.py
    │   └── kf.py            # Kalman filter implementation
    ├── gazebo.py            # Gazebo simulation launcher
    └── ros2py_py2ros.py     # Message conversion utilities (requires ROS2)

docs/
├── source/
│   ├── notebooks/           # Implementation notebooks (built to HTML)
│   │   ├── standard_kf.ipynb
│   │   ├── kf_turtlebot_demo.ipynb
│   │   └── crazyflie_kf_demo.ipynb
│   ├── references.bib       # Bibliography with impl_* fields
│   └── _static/js/
│       └── bib_metadata.js  # Auto-generated from references.bib
├── generate_bib_metadata.py # Regenerates bib_metadata.js
└── build/html/              # Generated documentation

tests/                       # Test directory (currently empty)
```

## Python Version

Requires Python >=3.12 (specified in pyproject.toml)

## Dependencies

Core: numpy, pandas, matplotlib, scipy
ROS2: rclpy, geometry_msgs, sensor_msgs, nav_msgs, std_msgs, turtlesim
Dev: pytest, pytest-doctestplus, black, isort, mypy, flake8, pylint
Docs: sphinx, sphinx-rtd-theme, nbsphinx, myst-parser

## Testing Philosophy

The project emphasizes doctests over unit tests. When adding new functionality:
- Include doctest examples in docstrings showing typical usage
- Use `NORMALIZE_WHITESPACE` and `ELLIPSIS` options (configured globally)
- Ensure examples are self-contained and demonstrate key features
