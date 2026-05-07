"""
dynamicalnodes: A modular Python framework for dynamical systems, estimation, and ROS2 integration.
"""

from .dynamical_system import DynamicalSystem
from .rosnode import ROSNode

# Lazy import — requires a live ROS2 installation
_ROS2_MODULES = {
    "ros2py_py2ros": ("ros2py_py2ros", None),
}


def __getattr__(name):
    if name in _ROS2_MODULES:
        module_name, attr = _ROS2_MODULES[name]
        try:
            import importlib
            mod = importlib.import_module(f".{module_name}", package=__name__)
            return mod if attr is None else getattr(mod, attr)
        except ImportError as e:
            raise ImportError(
                f"{name} requires ROS2 dependencies. Install with: pip install dynamicalnodes[ros2]\n"
                f"Original error: {e}"
            ) from e
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["DynamicalSystem", "ROSNode"]
