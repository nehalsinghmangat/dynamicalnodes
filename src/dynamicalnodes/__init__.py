"""
dynamicalnodes: A modular Python framework for dynamical systems, estimation, and ROS2 integration.
"""

from .dynamical_system import DynamicalSystem
from . import rostools

# Lazy imports for ROS2-dependent symbols — only fail if actually used
def __getattr__(name):
    if name == "ROSNode":
        try:
            from .rosnode import ROSNode
            return ROSNode
        except ImportError as e:
            raise ImportError(
                f"ROSNode requires ROS2 dependencies. Install with: pip install dynamicalnodes[ros2]\n"
                f"Original error: {e}"
            ) from e
    if name == "reset_ros":
        try:
            from .rostools import reset_ros
            return reset_ros
        except ImportError as e:
            raise ImportError(
                f"reset_ros requires ROS2 dependencies. Install with: pip install dynamicalnodes[ros2]\n"
                f"Original error: {e}"
            ) from e
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "DynamicalSystem",
    "ROSNode",
    "reset_ros",
    "rostools",
]
