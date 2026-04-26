"""
ROS2 node wrapper for deploying dynamical systems as real-time control nodes.

This module provides ROSNode, which wraps a DynamicalSystem as a ROS2 node,
enabling seamless deployment from pure Python development to simulation and
hardware. Key features include:

- **Event-driven processing**: step() runs immediately when messages arrive
- **Sync modes**: "any" (default) or "all" for multi-sensor coordination
- **Automatic message conversion**: ROS messages <-> NumPy arrays via registered converters
- **Staleness enforcement**: stale inputs are dropped — step() only sees fresh data
- **Immediate publishing**: outputs are published on every step()
- **Thread-safe operation**: Background executor with proper synchronization

Example
-------
Deploy a Kalman filter as a ROS2 estimator node:

>>> from geometry_msgs.msg import Twist
>>> from nav_msgs.msg import Odometry
>>> from dynamicalnodes import DynamicalSystem, ROSNode
>>>
>>> def f_kf(xk, odom, cmd_vel):
...     # ... Kalman predict/update ...
...     return x_new
>>>
>>> def h_kf(xk):
...     return xk
>>>
>>> filter_sys = DynamicalSystem(f=f_kf, h=h_kf)
>>> estimator = ROSNode(
...     node_name="state_estimator",
...     dynamical_system=filter_sys,
...     subscribes_to=[
...         {"topic": "/odom",    "msg_type": Odometry, "arg": "odom",    "stale_after": 0.1},
...         {"topic": "/cmd_vel", "msg_type": Twist,    "arg": "cmd_vel", "stale_after": 0.1},
...     ],
...     publishes_to=[
...         {"topic": "/state_estimate", "msg_type": Odometry},
...     ],
...     sync_mode="any",
... )
>>> estimator.start(initial_state=x0)  # doctest: +SKIP

See Also
--------
DynamicalSystem : Core abstraction for modeling control components
ros2py_py2ros : Message conversion utilities
"""

from collections import deque
from typing import Dict, Optional, Sequence, Tuple, Any, List, Deque
import numpy as np
import threading
import time

from dynamicalnodes.dynamical_system import DynamicalSystem
import rclpy
from rclpy.node import Node
from rclpy.executors import SingleThreadedExecutor, Executor
from rclpy.qos import QoSProfile, QoSHistoryPolicy, QoSReliabilityPolicy
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.time import Time
from numpy.typing import NDArray

from dynamicalnodes.ros2py_py2ros import ROS2PY_DEFAULT, PY2ROS_DEFAULT

#: Type alias for subscription configuration dict
SubDict = Dict[str, Any]

#: Type alias for publication configuration dict
PubDict = Dict[str, Any]


class ROSNode:
    """
    Wraps a DynamicalSystem as a ROS2 node with event-driven processing.

    Outputs are published immediately on every step(). Stale inputs are
    dropped — step() only receives arguments whose data arrived within
    their ``stale_after`` window.

    Parameters
    ----------
    node_name : str
        Name of the ROS2 node.
    dynamical_system : DynamicalSystem
        The dynamical system to step when messages arrive.
    subscribes_to : list of dict, optional
        Subscription configurations. Each dict supports:

        - ``"topic"`` (str): ROS topic name
        - ``"msg_type"`` (type): ROS message class
        - ``"arg"`` (str): Python argument name passed to step()
        - ``"stale_after"`` (float, optional): Seconds before a message is
          considered stale and dropped. Omit to never expire.
        - ``"buffer_size"`` (int, optional): Max queued messages (default 1).
        - ``"ros2py"`` (Callable, optional): Custom converter; falls back to
          ``ROS2PY_DEFAULT``.

    publishes_to : list of dict, optional
        Publication configurations. Each dict supports:

        - ``"topic"`` (str): ROS topic name
        - ``"msg_type"`` (type): ROS message class
        - ``"key"`` (str, optional): Key in h() return dict. Required when
          h() returns a dict with multiple outputs.
        - ``"py2ros"`` (Callable, optional): Custom converter; falls back to
          ``PY2ROS_DEFAULT``.

    sync_mode : str, default ``"any"``
        - ``"any"``: step() runs when **any** subscription receives a message.
          Stale inputs for other subscriptions are simply omitted.
        - ``"all"``: step() runs only when **all** subscriptions have data
          within their ``stale_after`` window.

    qos_profile : QoSProfile, optional
        ROS2 QoS profile for all subscriptions and publishers.

    Examples
    --------
    >>> from sensor_msgs.msg import Imu
    >>> from geometry_msgs.msg import Twist
    >>>
    >>> system = DynamicalSystem(h=lambda imu: imu * 0.1)
    >>> node = ROSNode(
    ...     node_name="processor",
    ...     dynamical_system=system,
    ...     subscribes_to=[{"topic": "/imu", "msg_type": Imu, "arg": "imu"}],
    ...     publishes_to=[{"topic": "/output", "msg_type": Twist}],
    ... )
    >>> node.start()  # doctest: +SKIP
    """

    def __init__(
        self,
        *,
        node_name: str,
        dynamical_system: DynamicalSystem,
        subscribes_to: Optional[Sequence[SubDict]] = None,
        publishes_to: Optional[Sequence[PubDict]] = None,
        sync_mode: str = "any",
        qos_profile: Optional[QoSProfile] = None,
    ) -> None:
        if sync_mode not in ("any", "all"):
            raise ValueError(f"sync_mode must be 'any' or 'all', got: {sync_mode!r}")

        # -------- Core config --------
        self._node_name = node_name
        self._dynamical_system = dynamical_system
        self._state: Optional[Any] = None
        self._params: Dict[str, Any] = {}
        self._sync_mode = sync_mode

        # Determine state parameter name from f's first argument
        self._state_param_name: Optional[str] = None
        if dynamical_system.f is not None:
            import inspect
            params = list(inspect.signature(dynamical_system.f).parameters.keys())
            if params:
                self._state_param_name = params[0]

        # -------- ROS objects (created in create_node) --------
        self._executor: Optional[Executor] = None
        self._thread: Optional[threading.Thread] = None
        self._node: Optional[Node] = None
        self._cb_group: Optional[ReentrantCallbackGroup] = None
        self._t0: Optional[Time] = None

        # -------- Threading state --------
        self._step_lock = threading.Lock()
        self._inputs_lock = threading.Lock()
        self._latest_output: Optional[Any] = None
        self._output_ready = threading.Event()

        # QoS profile
        self._qos = qos_profile or QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=QoSReliabilityPolicy.RELIABLE,
        )

        # -------- Parse subscriptions --------
        # Stored as: [(topic, msg_type, ros2py, arg_name, stale_after, buffer_size), ...]
        self._subs: List[Tuple[str, type, Any, str, Optional[float], int]] = []
        for sub_dict in subscribes_to or []:
            if not isinstance(sub_dict, dict):
                raise TypeError("Each subscription must be a dict")

            topic      = sub_dict.get("topic")
            msg_type   = sub_dict.get("msg_type")
            arg_name   = sub_dict.get("arg")
            ros2py     = sub_dict.get("ros2py")
            stale_after = sub_dict.get("stale_after")
            buffer_size = sub_dict.get("buffer_size", 1)

            if not topic or not isinstance(topic, str):
                raise ValueError(f"Subscription missing 'topic': {sub_dict}")
            if msg_type is None or not isinstance(msg_type, type):
                raise TypeError(f"Subscription 'msg_type' must be a class: {sub_dict}")
            if not arg_name or not isinstance(arg_name, str):
                raise ValueError(f"Subscription missing 'arg': {sub_dict}")
            if not isinstance(buffer_size, int) or buffer_size < 1:
                raise ValueError(f"buffer_size must be a positive integer: {sub_dict}")

            if ros2py is None:
                ros2py = ROS2PY_DEFAULT.get(msg_type)
                if ros2py is None:
                    raise TypeError(
                        f"No ros2py converter for {msg_type.__name__!r} on '{topic}'. "
                        f"Provide 'ros2py' or add to ROS2PY_DEFAULT."
                    )

            self._subs.append((
                topic, msg_type, ros2py, arg_name,
                float(stale_after) if stale_after else None,
                int(buffer_size),
            ))

        sub_topics = [t for t, *_ in self._subs]
        if len(sub_topics) != len(set(sub_topics)):
            dup = sorted({t for t in sub_topics if sub_topics.count(t) > 1})
            raise ValueError(f"Duplicate subscribe topics: {dup}")

        self._topic_to_arg: Dict[str, str] = {t: a for t, _, _, a, _, _ in self._subs}
        self._arg_to_topic: Dict[str, str] = {a: t for t, _, _, a, _, _ in self._subs}
        # arg -> stale_after threshold (None = never expires)
        self._arg_stale_after: Dict[str, Optional[float]] = {
            a: s for _, _, _, a, s, _ in self._subs
        }

        # Incoming queues: arg_name -> deque of (enqueue_timestamp, value)
        self._input_queues: Dict[str, Deque[Tuple[float, NDArray]]] = {
            a: deque(maxlen=buf) for _, _, _, a, _, buf in self._subs
        }

        # -------- Parse publications --------
        # Stored as: [(topic, msg_type, py2ros, key), ...]
        self._pubs_cfg: List[Tuple[str, type, Any, Optional[str]]] = []
        # Runtime (after create_node): [(topic, msg_type, py2ros, key, pub), ...]
        self._pubs: List[Tuple[str, type, Any, Optional[str], Any]] = []

        for pub_dict in publishes_to or []:
            if not isinstance(pub_dict, dict):
                raise TypeError("Each publication must be a dict")

            topic    = pub_dict.get("topic")
            msg_type = pub_dict.get("msg_type")
            key      = pub_dict.get("key")
            py2ros   = pub_dict.get("py2ros")

            if not topic or not isinstance(topic, str):
                raise ValueError(f"Publication missing 'topic': {pub_dict}")
            if msg_type is None or not isinstance(msg_type, type):
                raise TypeError(f"Publication 'msg_type' must be a class: {pub_dict}")

            if py2ros is None:
                py2ros = PY2ROS_DEFAULT.get(msg_type)
                if py2ros is None:
                    raise TypeError(
                        f"No py2ros converter for {msg_type.__name__!r} on '{topic}'. "
                        f"Provide 'py2ros' or add to PY2ROS_DEFAULT."
                    )

            self._pubs_cfg.append((topic, msg_type, py2ros, key))

        if len(self._pubs_cfg) > 1:
            if any(k is None for _, _, _, k in self._pubs_cfg):
                raise ValueError(
                    "When using multiple publishers, all must have 'key' specified."
                )

    # --------------------------------------------------------------------------
    # NODE CREATION
    # --------------------------------------------------------------------------
    def create_node(self) -> Node:
        """
        Create the underlying rclpy.Node, subscriptions, and publishers.

        Returns
        -------
        Node
            The created (or existing) rclpy.Node instance.
        """
        if self._node is not None:
            return self._node

        if not rclpy.ok():  # type: ignore[attr-defined]
            rclpy.init()

        node = Node(self._node_name)
        self._node = node
        self._cb_group = ReentrantCallbackGroup()
        self._t0 = node.get_clock().now()

        for topic, msg_type, ros2py, arg_name, _, _ in self._subs:
            node.create_subscription(
                msg_type, topic,
                self._make_sub_cb(topic, ros2py, arg_name),
                self._qos,
                callback_group=self._cb_group,
            )

        self._pubs.clear()
        for topic, msg_type, py2ros, key in self._pubs_cfg:
            pub = node.create_publisher(msg_type, topic, self._qos)
            self._pubs.append((topic, msg_type, py2ros, key, pub))

        node.get_logger().info(
            f"[{node.get_name()}] "
            f"subs={list(self._topic_to_arg)} "
            f"pubs={[t for t, *_ in self._pubs] or None} "
            f"sync_mode={self._sync_mode}"
        )
        return node

    # --------------------------------------------------------------------------
    # SUBSCRIPTION CALLBACK (event-driven)
    # --------------------------------------------------------------------------
    def _make_sub_cb(self, topic: str, ros2py: Any, arg_name: str):
        def _cb(msg):
            node = self._node
            if node is None:
                return
            try:
                arr = np.asarray(ros2py(msg), dtype=float)
                if arr.ndim == 0:
                    arr = arr[None]
                now = time.monotonic()
                with self._inputs_lock:
                    self._input_queues[arg_name].append((now, arr))
                if self._should_step():
                    self._run_step()
            except Exception as e:
                node.get_logger().error(f"[{topic}] callback error: {e}")

        return _cb

    def _should_step(self) -> bool:
        return True if self._sync_mode == "any" else self._all_fresh()

    def _all_fresh(self) -> bool:
        """Return True if every subscription has data within its stale_after window."""
        now = time.monotonic()
        with self._inputs_lock:
            for arg_name, stale_after in self._arg_stale_after.items():
                q = self._input_queues.get(arg_name)
                if not q:
                    return False
                if stale_after is not None and (now - q[-1][0]) > stale_after:
                    return False
        return True

    def _run_step(self) -> None:
        node = self._node
        if node is None or self._t0 is None:
            return

        with self._step_lock:
            try:
                inputs = self._build_inputs_snapshot()
                tk = (node.get_clock().now() - self._t0).nanoseconds * 1e-9
                step_kwargs = {"tk": tk, **self._params, **inputs}

                if self._state_param_name is not None and self._state is not None:
                    step_kwargs[self._state_param_name] = self._state

                result = self._dynamical_system.step(**step_kwargs)

                if self._dynamical_system.f is not None:
                    self._state, yk = result
                else:
                    yk = result

                self._latest_output = yk
                self._output_ready.set()

                for topic, _, py2ros, key, pub in self._pubs:
                    value = yk[key] if (key is not None and isinstance(yk, dict)) else yk
                    if key is not None and not (isinstance(yk, dict) and key in yk):
                        continue
                    self._publish_value(topic, pub, py2ros, value)

            except Exception as e:
                node.get_logger().error(f"step() error: {e}")

    def _build_inputs_snapshot(self) -> Dict[str, NDArray]:
        """Drain stale entries and return a snapshot of current fresh inputs."""
        now = time.monotonic()
        inputs: Dict[str, NDArray] = {}
        with self._inputs_lock:
            for arg_name, stale_after in self._arg_stale_after.items():
                q = self._input_queues.get(arg_name)
                if q is None:
                    continue
                if stale_after is not None:
                    while q and (now - q[0][0]) > stale_after:
                        q.popleft()
                if q:
                    inputs[arg_name] = q[-1][1].copy()
        return inputs

    # --------------------------------------------------------------------------
    # PUBLISHING
    # --------------------------------------------------------------------------
    def _publish_value(self, topic: str, pub: Any, py2ros: Any, value: Any) -> None:
        node = self._node
        if node is None:
            return
        try:
            pub.publish(py2ros(np.asarray(value, dtype=float).ravel()))
        except Exception as e:
            node.get_logger().error(f"[{topic}] publish failed: {e}")

    # --------------------------------------------------------------------------
    # CONTROL API
    # --------------------------------------------------------------------------
    def start(
        self,
        initial_state: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Start spinning the ROS node in a background thread.

        Parameters
        ----------
        initial_state : Any, optional
            Initial state for the dynamical system.
        params : dict, optional
            Static parameters merged into every step() call.
        """
        if self.is_running():
            return
        self._state = initial_state
        self._params = dict(params or {})
        self._latest_output = None
        self._output_ready.clear()

        node = self._node or self.create_node()
        executor = SingleThreadedExecutor()
        executor.add_node(node)
        self._executor = executor
        self._thread = threading.Thread(target=executor.spin, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop spinning the executor without destroying the node."""
        if self._executor:
            try:
                self._executor.shutdown()
            except Exception:
                pass
            self._executor = None
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None

    def destroy(self) -> None:
        """Stop the executor and remove the node from the ROS graph."""
        self.stop()
        if self._node:
            try:
                self._node.destroy_node()
            except Exception:
                pass
            self._node = None
        self._pubs.clear()
        for q in self._input_queues.values():
            q.clear()
        self._t0 = None

    def is_running(self) -> bool:
        """Return True if the background spin thread is alive."""
        return self._thread is not None and self._thread.is_alive()

    def latest_inputs(self) -> Dict[str, np.ndarray]:
        """Return the most recently received value for each subscription arg."""
        with self._inputs_lock:
            return {k: np.asarray(q[-1][1]) for k, q in self._input_queues.items() if q}

    @property
    def state(self) -> Any:
        """Current state of the dynamical system."""
        return self._state

    # --------------------------------------------------------------------------
    # SIMULATION API (for use without ROS2)
    # --------------------------------------------------------------------------
    def step(self, **kwargs: Any) -> Any:
        """
        Simulate one step without ROS2.

        Pass all inputs as keyword arguments. Subscription inputs are
        identified by their ``arg`` name and converted if needed. Stale
        inputs are dropped; step() only receives fresh data.

        Parameters
        ----------
        **kwargs : Any
            - ``tk`` (float): simulated time in seconds (default 0.0).
            - Subscription arg names: ROS messages or NumPy arrays.
            - Any extra parameters forwarded verbatim to the dynamical system.

        Returns
        -------
        Any
            - Single publisher: the ROS message produced by h().
            - Multiple publishers: ``{topic: msg}`` dict.
            - No publishers: raw output from h().
            - ``None`` if sync_mode="all" and not all inputs are fresh.

        Examples
        --------
        Simulate a reference -> plant chain:

        >>> import numpy as np
        >>> from dynamicalnodes import DynamicalSystem, ROSNode
        >>> from std_msgs.msg import Float64
        >>>
        >>> ref_sys = DynamicalSystem(h=lambda: np.array([1.0]))
        >>> ref_node = ROSNode(
        ...     node_name="ref",
        ...     dynamical_system=ref_sys,
        ...     publishes_to=[{"topic": "/u_k", "msg_type": Float64}],
        ... )
        >>>
        >>> def plant_f(xk, u_k):
        ...     return xk + 0.1 * u_k
        >>> plant_sys = DynamicalSystem(f=plant_f, h=lambda xk: xk)
        >>> plant_node = ROSNode(
        ...     node_name="plant",
        ...     dynamical_system=plant_sys,
        ...     subscribes_to=[{"topic": "/u_k", "msg_type": Float64, "arg": "u_k"}],
        ...     publishes_to=[{"topic": "/y_k", "msg_type": Float64}],
        ... )
        >>>
        >>> plant_node._state = np.array([0.0])
        >>> for k in range(3):
        ...     tk = k * 0.1
        ...     u_msg = ref_node.step(tk=tk)
        ...     y_msg = plant_node.step(tk=tk, u_k=u_msg)
        ...     print(f"k={k}: y={y_msg.data:.2f}")
        k=0: y=0.00
        k=1: y=0.10
        k=2: y=0.20
        """
        tk: float = kwargs.get("tk", 0.0)
        sub_arg_names = {a for _, _, _, a, _, _ in self._subs}
        extra_params: Dict[str, Any] = {}

        for arg_name, value in kwargs.items():
            if arg_name == "tk" or value is None:
                continue
            if arg_name not in sub_arg_names:
                extra_params[arg_name] = value
                continue

            ros2py = next((c for _, _, c, a, _, _ in self._subs if a == arg_name), None)

            if hasattr(value, "__slots__") or hasattr(value, "_fields_and_field_types"):
                if ros2py is None:
                    raise ValueError(f"No ros2py converter for arg '{arg_name}'")
                arr = np.asarray(ros2py(value), dtype=float)
            else:
                arr = np.asarray(value, dtype=float)

            if arr.ndim == 0:
                arr = arr[None]
            self._input_queues[arg_name].append((tk, arr))

        if self._sync_mode == "all" and not self._all_fresh_sim(tk):
            return None

        step_inputs = self._build_inputs_snapshot_sim(tk)
        if not step_inputs and self._subs:
            return None

        step_kwargs = {"tk": tk, **self._params, **extra_params, **step_inputs}
        if self._state_param_name is not None and self._state is not None:
            step_kwargs[self._state_param_name] = self._state

        result = self._dynamical_system.step(**step_kwargs)
        if self._dynamical_system.f is not None:
            self._state, yk = result
        else:
            yk = result

        if not self._pubs_cfg:
            return yk

        output: Dict[str, Any] = {}
        for topic, _, py2ros, key in self._pubs_cfg:
            if key is not None:
                if not (isinstance(yk, dict) and key in yk):
                    continue
                value = yk[key]
            else:
                value = yk
            output[topic] = py2ros(np.asarray(value, dtype=float).ravel())

        if not output:
            return None
        return list(output.values())[0] if len(self._pubs_cfg) == 1 else output

    def _all_fresh_sim(self, tk: float) -> bool:
        """Return True if all subscriptions have fresh data at simulated time tk."""
        for arg_name, stale_after in self._arg_stale_after.items():
            q = self._input_queues.get(arg_name)
            if not q:
                return False
            if stale_after is not None and (tk - q[-1][0]) > stale_after:
                return False
        return True

    def _build_inputs_snapshot_sim(self, tk: float) -> Dict[str, NDArray]:
        """Build inputs snapshot at simulated time tk; stale entries are dropped."""
        inputs: Dict[str, NDArray] = {}
        for arg_name, stale_after in self._arg_stale_after.items():
            q = self._input_queues.get(arg_name)
            if q is None:
                continue
            if stale_after is not None:
                while q and (tk - q[0][0]) > stale_after:
                    q.popleft()
            if q:
                inputs[arg_name] = q[-1][1].copy()
        return inputs

    def reset_simulation(self) -> None:
        """
        Reset simulation state for a new run.

        Clears input queues and the dynamical system state.

        Examples
        --------
        >>> from dynamicalnodes import DynamicalSystem, ROSNode
        >>> from std_msgs.msg import Float64
        >>> import numpy as np
        >>>
        >>> sys = DynamicalSystem(f=lambda x: x + 1, h=lambda x: x)
        >>> node = ROSNode(
        ...     node_name="test",
        ...     dynamical_system=sys,
        ...     publishes_to=[{"topic": "/out", "msg_type": Float64}],
        ... )
        >>> node._state = np.array([0.0])
        >>> _ = node.step(tk=0.0)
        >>> node._state
        array([1.])
        >>> node.reset_simulation()
        >>> node._state is None
        True
        """
        for q in self._input_queues.values():
            q.clear()
        self._state = None
