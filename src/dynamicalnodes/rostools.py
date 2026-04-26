"""
ROS2 quality-of-life utilities for Jupyter notebooks.

Provides helpers to inspect the live ROS2 graph, capture topic data,
and launch GUI tools — all from within a notebook kernel.
"""

import itertools
import subprocess
import threading
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple

_node_counter = itertools.count()


# ---------------------------------------------------------------------------
# Context management
# ---------------------------------------------------------------------------

def reset_ros() -> None:
    """
    Reset the ROS2 context to a clean state.

    Safely shuts down any existing rclpy context and reinitializes it.
    Useful in Jupyter notebooks when re-running cells or recovering from
    errors. Any existing ROSNode objects become invalid after this call.

    Examples
    --------
    >>> from dynamicalnodes.rostools import reset_ros
    >>> reset_ros()  # doctest: +SKIP
    """
    import rclpy

    try:
        if rclpy.ok():
            rclpy.shutdown()
    except Exception:
        pass
    try:
        rclpy.init()
    except Exception:
        pass


@contextmanager
def _tmp_node(name: Optional[str] = None):
    """Yield a short-lived rclpy.Node for graph queries, then destroy it."""
    import rclpy
    from rclpy.node import Node

    if not rclpy.ok():
        rclpy.init()
    node_name = name or f"_dn_util_{next(_node_counter)}"
    node = Node(node_name)
    try:
        yield node
    finally:
        node.destroy_node()


# ---------------------------------------------------------------------------
# Graph inspection
# ---------------------------------------------------------------------------

def list_nodes() -> List[str]:
    """
    Return fully-qualified names of all live ROS2 nodes.

    Returns
    -------
    list of str
        Node names like ``['/turtlesim', '/teleop_turtle']``.

    Examples
    --------
    >>> from dynamicalnodes.rostools import list_nodes
    >>> nodes = list_nodes()  # doctest: +SKIP
    """
    with _tmp_node() as node:
        pairs = node.get_node_names_and_namespaces()
    result = []
    for name, ns in pairs:
        fqn = (ns.rstrip("/") + "/" + name)
        result.append(fqn if fqn.startswith("/") else "/" + fqn)
    return result


def list_topics() -> List[Tuple[str, List[str]]]:
    """
    Return all active ROS2 topics with their message types.

    Returns
    -------
    list of (str, list of str)
        Each entry is ``(topic_name, [type_string, ...])``.

    Examples
    --------
    >>> from dynamicalnodes.rostools import list_topics
    >>> for name, types in list_topics():  # doctest: +SKIP
    ...     print(name, types)
    /cmd_vel ['geometry_msgs/msg/Twist']
    /odom    ['nav_msgs/msg/Odometry']
    """
    with _tmp_node() as node:
        return list(node.get_topic_names_and_types())


def list_services() -> List[Tuple[str, List[str]]]:
    """
    Return all active ROS2 services with their types.

    Returns
    -------
    list of (str, list of str)
        Each entry is ``(service_name, [type_string, ...])``.
    """
    with _tmp_node() as node:
        return list(node.get_service_names_and_types())


def node_info(node_name: str) -> Dict[str, Any]:
    """
    Return subscription, publication, and service info for a node.

    Parameters
    ----------
    node_name : str
        Fully-qualified node name, e.g. ``'/state_estimator'``.
        Leading slash is optional.

    Returns
    -------
    dict
        Keys: ``'subscriptions'``, ``'publications'``, ``'services'``,
        each a list of ``(name, [type_string])`` tuples.

    Examples
    --------
    >>> from dynamicalnodes.rostools import node_info
    >>> info = node_info('/turtlesim')            # doctest: +SKIP
    >>> info['subscriptions']                     # doctest: +SKIP
    [('/turtle1/cmd_vel', ['geometry_msgs/msg/Twist'])]
    """
    stripped = node_name.lstrip("/")
    if "/" in stripped:
        ns_part, bare = stripped.rsplit("/", 1)
        ns = "/" + ns_part
    else:
        ns, bare = "/", stripped

    with _tmp_node() as node:
        subs = node.get_subscriber_names_and_types_by_node(bare, ns)
        pubs = node.get_publisher_names_and_types_by_node(bare, ns)
        svcs = node.get_service_names_and_types_by_node(bare, ns)

    return {
        "subscriptions": list(subs),
        "publications": list(pubs),
        "services": list(svcs),
    }


def topic_info(topic_name: str) -> Dict[str, Any]:
    """
    Return type, publisher count, and subscriber count for a topic.

    Parameters
    ----------
    topic_name : str
        ROS topic name, e.g. ``'/odom'``.

    Returns
    -------
    dict
        Keys: ``'types'`` (list of str), ``'publisher_count'`` (int),
        ``'subscriber_count'`` (int).

    Examples
    --------
    >>> from dynamicalnodes.rostools import topic_info
    >>> topic_info('/odom')  # doctest: +SKIP
    {'types': ['nav_msgs/msg/Odometry'], 'publisher_count': 1, 'subscriber_count': 2}
    """
    with _tmp_node() as node:
        all_topics = dict(node.get_topic_names_and_types())
        types = all_topics.get(topic_name, [])
        pub_count = node.count_publishers(topic_name)
        sub_count = node.count_subscribers(topic_name)

    return {
        "types": types,
        "publisher_count": pub_count,
        "subscriber_count": sub_count,
    }


# ---------------------------------------------------------------------------
# Message capture
# ---------------------------------------------------------------------------

def echo(
    topic: str,
    msg_type,
    *,
    n: int = 1,
    timeout: float = 5.0,
) -> List[Any]:
    """
    Capture *n* messages from a topic and return as a list.

    Messages are converted to NumPy arrays via ``ROS2PY_DEFAULT`` when a
    converter is registered; otherwise the raw ROS message is returned.

    Parameters
    ----------
    topic : str
        ROS topic name, e.g. ``'/odom'``.
    msg_type : type
        ROS message class, e.g. ``nav_msgs.msg.Odometry``.
    n : int, default 1
        Number of messages to collect before returning.
    timeout : float, default 5.0
        Maximum seconds to wait. Returns whatever was collected so far.

    Returns
    -------
    list
        NumPy arrays (if converter exists) or raw ROS messages.
        May contain fewer than *n* items if timeout expires.

    Examples
    --------
    >>> from dynamicalnodes.rostools import echo
    >>> from nav_msgs.msg import Odometry
    >>> msgs = echo('/odom', Odometry, n=3, timeout=2.0)  # doctest: +SKIP
    >>> msgs[0].shape  # doctest: +SKIP
    (13,)
    """
    import rclpy
    from rclpy.node import Node
    from rclpy.executors import SingleThreadedExecutor

    try:
        from dynamicalnodes.ros2py_py2ros import ROS2PY_DEFAULT
        converter = ROS2PY_DEFAULT.get(msg_type)
    except ImportError:
        converter = None

    if not rclpy.ok():
        rclpy.init()

    collected: List[Any] = []
    done = threading.Event()

    def _cb(msg):
        collected.append(converter(msg) if converter else msg)
        if len(collected) >= n:
            done.set()

    node_name = f"_dn_echo_{next(_node_counter)}"
    node = Node(node_name)
    node.create_subscription(msg_type, topic, _cb, 10)

    executor = SingleThreadedExecutor()
    executor.add_node(node)

    def _spin():
        while not done.is_set():
            executor.spin_once(timeout_sec=0.05)

    t = threading.Thread(target=_spin, daemon=True)
    t.start()
    done.wait(timeout=timeout)

    executor.shutdown(timeout_sec=0.0)
    node.destroy_node()

    return collected


# ---------------------------------------------------------------------------
# GUI launchers
# ---------------------------------------------------------------------------

def rqt_graph(*, args: Optional[List[str]] = None) -> subprocess.Popen:
    """
    Launch ``rqt_graph`` in the background.

    Parameters
    ----------
    args : list of str, optional
        Extra CLI arguments forwarded to rqt_graph.

    Returns
    -------
    subprocess.Popen
        Process handle. Call ``.terminate()`` to close the window.

    Examples
    --------
    >>> from dynamicalnodes.rostools import rqt_graph
    >>> proc = rqt_graph()  # doctest: +SKIP
    >>> proc.terminate()    # doctest: +SKIP
    """
    cmd = ["rqt_graph"] + (args or [])
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def rqt(plugin: str = "", *, args: Optional[List[str]] = None) -> subprocess.Popen:
    """
    Launch ``rqt`` or a specific plugin in the background.

    Parameters
    ----------
    plugin : str, optional
        Plugin name to open, e.g. ``'rqt_plot'``, ``'rqt_console'``,
        ``'rqt_topic'``, ``'rqt_image_view'``.
    args : list of str, optional
        Extra CLI arguments.

    Returns
    -------
    subprocess.Popen
        Process handle.

    Examples
    --------
    >>> from dynamicalnodes.rostools import rqt
    >>> proc = rqt('rqt_plot')  # doctest: +SKIP
    >>> proc.terminate()         # doctest: +SKIP
    """
    cmd = ["rqt"]
    if plugin:
        cmd += ["--standalone", plugin]
    cmd += args or []
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def rviz2(
    config: Optional[str] = None,
    *,
    args: Optional[List[str]] = None,
) -> subprocess.Popen:
    """
    Launch ``rviz2`` in the background.

    Parameters
    ----------
    config : str, optional
        Path to a ``.rviz`` config file.
    args : list of str, optional
        Extra CLI arguments.

    Returns
    -------
    subprocess.Popen
        Process handle.

    Examples
    --------
    >>> from dynamicalnodes.rostools import rviz2
    >>> proc = rviz2()    # doctest: +SKIP
    >>> proc.terminate()  # doctest: +SKIP
    """
    cmd = ["rviz2"]
    if config:
        cmd += ["-d", config]
    cmd += args or []
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
