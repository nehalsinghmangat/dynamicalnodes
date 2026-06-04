"""
ROSNode wrapper for simulation and ROS2 deployment.

Two workflows:

**Simulation** — call ``step()`` directly in Python or Jupyter notebooks to test ros2py and/or py2ros translation functions.
No ROS2 installation required.

**Deployment** — call ``write_ROSNode_to_rclpy(path)`` to emit a self-contained
``.py`` file that spins up a native rclpy node.  Every ROS2 detail (QoS profiles,
buffer depths, subscription callbacks, executor setup, etc...) is written out explicitly and
can be modified as needed. The ``.py`` file also has no runtime dependency on dynamicalnodes beyond ``DynamicalSystem`` and whatever dependencies the
f/h functions may have.

See Also
--------
DynamicalSystem : Core abstraction for modeling control components.
ros2py_py2ros   : Message conversion utilities (ros2py_* / py2ros_* functions).
"""

from typing import Dict, Optional, Sequence, Tuple, Any, List
import inspect
import numpy as np

from dynamicalnodes.dynamical_system import DynamicalSystem


#: Type alias for subscription configuration dict
SubDict = Dict[str, Any]

#: Type alias for publication configuration dict
PubDict = Dict[str, Any]


class ROSNode:
    """
    Wraps a DynamicalSystem for simulation and ROS2 deployment.

    Use ``step()`` for notebook simulation; use ``write_ROSNode_to_rclpy()`` to
    generate a deployable rclpy node.

    Parameters
    ----------
    dynamical_system : DynamicalSystem
        The dynamical system to step.
    subscribes_to : list of dict, optional
        Each dict:

        - ``"topic"`` (str): ROS topic name.
        - ``"msg_type"`` (type): ROS message class.
        - ``"arg"`` (str): kwarg name passed to step().
        - ``"ros2py"`` (Callable): ROS msg → NumPy array converter.
          Import from ``dynamicalnodes.ros2py_py2ros`` or write your own.
        - ``"stale_after"`` (float, optional): Seconds before data expires.
        - ``"buffer_size"`` (int, optional): Queue depth (default 1).
        - ``"use_msg_timestamp"`` (bool, optional): When ``True``, the
          subscription buffer stores the message's own ``header.stamp``
          as the timestamp instead of ROS-clock arrival time.  Only
          valid for message types that have a ``header`` field.  Useful
          when staleness should be relative to data *capture* time
          rather than network-arrival time (e.g. sensor fusion, bag
          replay).  Defaults to ``False``.

    publishes_to : list of dict, optional
        Each dict:

        - ``"topic"`` (str): ROS topic name.
        - ``"msg_type"`` (type): ROS message class.
        - ``"py2ros"`` (Callable): NumPy array → ROS msg converter.
          Import from ``dynamicalnodes.ros2py_py2ros``.
        - ``"key"`` (str, optional): Key into h() return dict. Required when
          h() returns a dict and there are multiple publishers.

    sync_mode : str, required when ``subscribes_to`` has more than one entry
        ``"any"`` — step whenever any subscription has fresh data.
        ``"all"`` — step only when every subscription has fresh data.

    state_name : str, optional
        Name of the state parameter in ``f``'s signature (e.g. ``"ck"`` for
        ``f(ck, ...)``) .  Required for stateful systems; ignored if ``f`` is
        ``None``.  ``step()`` injects ``self._state`` under this name before
        calling ``DynamicalSystem.step()``.

    timer_hz : float, optional
        In the generated node: fires ``_run_step`` at this frequency instead
        of triggering from subscription callbacks.

    Examples
    --------
    Stateless filter (no state, single subscriber):

    >>> from dynamicalnodes import DynamicalSystem, ROSNode
    >>> from std_msgs.msg import Float64
    >>> from dynamicalnodes.ros2py_py2ros import ros2py_float64, py2ros_float64
    >>> import numpy as np
    >>>
    >>> smoother = DynamicalSystem(h=lambda imu: imu * 0.5)
    >>> node = ROSNode(
    ...     dynamical_system=smoother,
    ...     subscribes_to=[{"topic": "/raw", "msg_type": Float64,
    ...                      "arg": "imu", "ros2py": ros2py_float64}],
    ...     publishes_to=[{"topic": "/smooth", "msg_type": Float64,
    ...                    "py2ros": py2ros_float64}],
    ... )
    >>> out = node.step(imu=np.array([2.0]))
    >>> out.data
    1.0
    """

    def __init__(
        self,
        *,
        dynamical_system: DynamicalSystem,
        state_name: Optional[str] = None,
        subscribes_to: Optional[Sequence[SubDict]] = None,
        publishes_to: Optional[Sequence[PubDict]] = None,
        sync_mode: Optional[str] = None,
        timer_hz: Optional[float] = None,
    ) -> None:
        n_subs = len(subscribes_to) if subscribes_to else 0
        if n_subs > 1 and sync_mode is None:
            raise ValueError(
                "sync_mode ('any' or 'all') is required when subscribes_to has "
                "more than one subscription"
            )
        sync_mode = sync_mode or "any"
        if sync_mode not in ("any", "all"):
            raise ValueError(f"sync_mode must be 'any' or 'all', got: {sync_mode!r}")
        if timer_hz is not None and timer_hz <= 0:
            raise ValueError(f"timer_hz must be positive, got {timer_hz}")

        self._dynamical_system = dynamical_system
        self._state: Optional[Any] = None
        self._state_key: Optional[str] = state_name
        self._sync_mode = sync_mode
        self._timer_hz = timer_hz

        # -------- Parse subscriptions --------
        self._subs: List[Tuple[str, type, Any, str, Optional[float], int, bool]] = []
        for sub_dict in subscribes_to or []:
            if not isinstance(sub_dict, dict):
                raise TypeError("Each subscription must be a dict")

            topic = sub_dict.get("topic")
            msg_type = sub_dict.get("msg_type")
            arg_name = sub_dict.get("arg")
            ros2py = sub_dict.get("ros2py")
            stale_after = sub_dict.get("stale_after")
            buffer_size = sub_dict.get("buffer_size", 1)
            use_msg_timestamp = bool(sub_dict.get("use_msg_timestamp", False))

            if not topic or not isinstance(topic, str):
                raise ValueError(f"Subscription missing 'topic': {sub_dict}")
            if msg_type is None or not isinstance(msg_type, type):
                raise TypeError(f"Subscription 'msg_type' must be a class: {sub_dict}")
            if not arg_name or not isinstance(arg_name, str):
                raise ValueError(f"Subscription missing 'arg': {sub_dict}")
            if not isinstance(buffer_size, int) or buffer_size < 1:
                raise ValueError(f"buffer_size must be a positive integer: {sub_dict}")
            if ros2py is None:
                raise TypeError(
                    f"'ros2py' converter required for subscriber '{arg_name}' "
                    f"(msg_type={msg_type.__name__!r}). "
                    f"Import from dynamicalnodes.ros2py_py2ros."
                )
            if use_msg_timestamp and "header" not in getattr(
                msg_type, "_fields_and_field_types", {}
            ):
                raise ValueError(
                    f"use_msg_timestamp=True for '{arg_name}' but "
                    f"{msg_type.__name__!r} has no 'header' field."
                )

            self._subs.append(
                (
                    topic,
                    msg_type,
                    ros2py,
                    arg_name,
                    float(stale_after) if stale_after else None,
                    int(buffer_size),
                    use_msg_timestamp,
                )
            )

        sub_topics = [t for t, *_ in self._subs]
        if len(sub_topics) != len(set(sub_topics)):
            dup = sorted({t for t in sub_topics if sub_topics.count(t) > 1})
            raise ValueError(f"Duplicate subscribe topics: {dup}")

        # -------- Parse publications --------
        self._pubs_cfg: List[Tuple[str, type, Any, Optional[str]]] = []
        for pub_dict in publishes_to or []:
            if not isinstance(pub_dict, dict):
                raise TypeError("Each publication must be a dict")

            topic = pub_dict.get("topic")
            msg_type = pub_dict.get("msg_type")
            key = pub_dict.get("key")
            py2ros = pub_dict.get("py2ros")

            if not topic or not isinstance(topic, str):
                raise ValueError(f"Publication missing 'topic': {pub_dict}")
            if msg_type is None or not isinstance(msg_type, type):
                raise TypeError(f"Publication 'msg_type' must be a class: {pub_dict}")
            if py2ros is None:
                raise TypeError(
                    f"'py2ros' converter required for publisher on '{topic}' "
                    f"(msg_type={msg_type.__name__!r}). "
                    f"Import from dynamicalnodes.ros2py_py2ros."
                )

            self._pubs_cfg.append((topic, msg_type, py2ros, key))

        if len(self._pubs_cfg) > 1:
            if any(k is None for _, _, _, k in self._pubs_cfg):
                raise ValueError(
                    "When using multiple publishers, all must have 'key' specified."
                )

    # --------------------------------------------------------------------------
    # SIMULATION API
    # --------------------------------------------------------------------------

    def step(self, **kwargs: Any) -> Any:
        """
        Simulate one step without ROS2.

        Converts ROS message inputs via their configured ``ros2py`` functions,
        steps the ``DynamicalSystem``, and converts the output via ``py2ros``.
        Use this to verify that message converters and system wiring are correct
        before deploying to ROS2.

        Parameters
        ----------
        **kwargs : Any
            - Subscription arg names: ROS messages or NumPy arrays.
            - Any extra parameters forwarded verbatim to the DynamicalSystem.

        Returns
        -------
        Any
            Single publisher: the ROS message from h().
            Multiple publishers: ``{topic: msg}`` dict.
            No publishers: raw h() output.

        Examples
        --------
        >>> import numpy as np
        >>> from dynamicalnodes import DynamicalSystem, ROSNode
        >>> from std_msgs.msg import Float64
        >>> from dynamicalnodes.ros2py_py2ros import ros2py_float64, py2ros_float64
        >>>
        >>> double = DynamicalSystem(h=lambda x: x * 2)
        >>> node = ROSNode(
        ...     dynamical_system=double,
        ...     subscribes_to=[{"topic": "/x", "msg_type": Float64,
        ...                      "arg": "x", "ros2py": ros2py_float64}],
        ...     publishes_to=[{"topic": "/y", "msg_type": Float64,
        ...                    "py2ros": py2ros_float64}],
        ... )
        >>> node.step(x=Float64(data=3.0)).data
        6.0
        """
        sub_arg_names = {a for _, _, _, a, _, _, _ in self._subs}
        step_kwargs: Dict[str, Any] = {}

        for arg_name, value in kwargs.items():
            if value is None:
                continue
            if arg_name in sub_arg_names:
                ros2py = next(
                    (c for _, _, c, a, _, _, _ in self._subs if a == arg_name), None
                )
                assert ros2py is not None
                if hasattr(value, "__slots__") or hasattr(
                    value, "_fields_and_field_types"
                ):
                    step_kwargs[arg_name] = np.asarray(ros2py(value), dtype=float)
                else:
                    step_kwargs[arg_name] = np.asarray(value, dtype=float)
            else:
                step_kwargs[arg_name] = value

        if self._state is not None and self._state_key is not None:
            step_kwargs[self._state_key] = self._state

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
                val = yk[key]
            else:
                val = yk
            output[topic] = py2ros(np.asarray(val, dtype=float).ravel())

        if not output:
            return None
        return list(output.values())[0] if len(self._pubs_cfg) == 1 else output

    @property
    def state(self) -> Any:
        """Current state of the dynamical system."""
        return self._state

    # --------------------------------------------------------------------------
    # DEPLOYMENT
    # --------------------------------------------------------------------------

    def write_ROSNode_to_rclpy(
        self,
        path: str,
        *,
        node_name: str,
        deps: Optional[List[Any]] = None,
        initial_state: Optional[Any] = None,
        initial_inputs: Optional[Dict[str, Any]] = None,
        static_params: Optional[Dict[str, Any]] = None,
        dynamic_params: Optional[Dict[str, Any]] = None,
        sub_noise: Optional[Dict[str, float]] = None,
        pub_noise: Optional[Dict[str, float]] = None,
    ) -> None:
        """
        Generate a standalone rclpy Python file that can be run with ``ros2 run``.

        The output file is a self-contained native rclpy node: QoS profiles,
        buffer depths, subscription callbacks, publisher calls, and executor
        setup are all written out explicitly in plain rclpy — exactly as a
        ROS2 developer would write them by hand.

        Parameters
        ----------
        path : str
            Destination file path (e.g. ``"my_controller_node.py"``).
        node_name : str
            ROS2 node name (used for the generated class name, ``super().__init__``,
            and logger messages).
        deps : list of callable, optional
            Helper functions that ``f`` or ``h`` depend on.  Each function's
            source is inlined before the dynamics functions in the output file.
            Use this when your notebook or module defines utility functions
            that ``f``/``h`` call internally.
        initial_state : Any, optional
            Embedded as ``self._state = ...`` in the generated node's
            ``__init__``.  Supports NumPy arrays and any ``repr()``-able value.
        static_params : dict, optional
            Parameters baked into the node at generation time.  Embedded as
            ``self._static_params = {...}`` and merged into every ``step()``
            call.  Use for values that never change after deployment.
        dynamic_params : dict, optional
            Parameters declared on the ROS2 parameter server with their
            default values.  Readable and writable at runtime via::

                ros2 param set /<node_name> <name> <value>

            Each key is emitted as ``declare_parameter(name, default)`` in
            ``__init__`` and read via ``get_parameter(name).value`` in every
            ``_run_step`` call.  Use for values you want to tune without
            restarting the node (e.g. controller gains).
        initial_inputs : dict, optional
            Cold-start fallback values for subscription inputs.  Keys must
            match subscription ``arg`` names.  A value is used only when the
            subscription buffer is completely empty — i.e. no message has
            ever arrived on that topic.  Once the first message arrives the
            subscription value takes over permanently.  If the subscription
            later goes stale the step is skipped (``None`` is not replaced),
            preventing silent operation on dead data.  Use this to break
            hard startup ordering dependencies between nodes.
        sub_noise : dict, optional
            Zero-mean Gaussian noise injected into subscription data after
            ros2py conversion.  Keys are topic strings; values are standard
            deviations (same units as the converted NumPy array).  Useful
            for robustness testing and hardware-in-the-loop simulation.
            Example: ``{"/yk": 0.1}`` adds noise with std=0.1 to ``/yk``.
        pub_noise : dict, optional
            Zero-mean Gaussian noise injected into publication data before
            py2ros conversion.  Same format as ``sub_noise``.
            Example: ``{"/uk": 50.0}`` adds noise with std=50 to ``/uk``.

        Raises
        ------
        ValueError
            If any function is a lambda (cannot be serialized).
        ValueError
            If the node has no subscriptions and no ``timer_hz`` — the
            generated node would never step.
        OSError
            If ``inspect.getsource()`` cannot retrieve a function's source
            (e.g. C extensions).  Use ``deps`` to wrap such functions.
        SyntaxError
            If the generated file contains invalid Python (indicates a bug
            in the generator).

        Notes
        -----
        **Function resolution**

        Functions from ``dynamicalnodes.ros2py_py2ros`` are emitted as import
        statements.  Functions from any other importable module (not
        ``__main__`` or an IPython cell) are also imported by name.  All other
        functions — typically those defined interactively in a notebook or
        script — are inlined verbatim via ``inspect.getsource()``.

        Examples
        --------
        >>> import numpy as np, tempfile, os
        >>> from dynamicalnodes import DynamicalSystem, ROSNode
        >>> from std_msgs.msg import Float64
        >>> from dynamicalnodes.ros2py_py2ros import ros2py_float64, py2ros_float64
        >>>
        >>> def f_plant(xk, u_k):
        ...     return xk + 0.1 * u_k
        >>> def h_plant(xk):
        ...     return xk
        >>>
        >>> sys = DynamicalSystem(f=f_plant, h=h_plant)
        >>> node = ROSNode(
        ...     dynamical_system=sys,
        ...     subscribes_to=[{"topic": "/u_k", "msg_type": Float64,
        ...                      "arg": "u_k", "ros2py": ros2py_float64,
        ...                      "stale_after": 0.5}],
        ...     publishes_to=[{"topic": "/y_k", "msg_type": Float64,
        ...                    "py2ros": py2ros_float64}],
        ... )
        >>> with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmp:
        ...     path = tmp.name
        >>> node.write_ROSNode_to_rclpy(path, node_name="plant",
        ...                             initial_state=np.array([0.0]))
        >>> content = open(path).read()
        >>> "def f_plant" in content and "def h_plant" in content
        True
        >>> "ros2py_float64" in content and "py2ros_float64" in content
        True
        >>> "create_subscription" in content and "create_publisher" in content
        True
        >>> "SingleThreadedExecutor" in content
        True
        >>> os.unlink(path)
        """
        import importlib
        import textwrap
        import re
        from pathlib import Path

        # ── local helpers ─────────────────────────────────────────────────────

        def _ident(topic: str) -> str:
            return re.sub(r"[^a-zA-Z0-9]+", "_", topic).strip("_") or "topic"

        def _class_name(name: str) -> str:
            return (
                "".join(w.capitalize() for w in re.split(r"[_\-\s]+", name) if w)
                + "Node"
            )

        def _repr_value(val: Any) -> str:
            if isinstance(val, np.ndarray):
                return f"np.array({val.tolist()!r})"
            if isinstance(val, tuple):
                inner = ", ".join(_repr_value(v) for v in val)
                return f"({inner},)" if len(val) == 1 else f"({inner})"
            if isinstance(val, list):
                return "[" + ", ".join(_repr_value(v) for v in val) + "]"
            if isinstance(val, dict):
                items = ", ".join(f"{k!r}: {_repr_value(v)}" for k, v in val.items())
                return "{" + items + "}"
            return repr(val)

        def _check_lambda(fn: Any, role: str) -> None:
            if fn is not None and getattr(fn, "__name__", None) == "<lambda>":
                raise ValueError(
                    f"{role} is a lambda — replace it with a named function "
                    f"so write_ROSNode_to_rclpy() can inline its source."
                )

        def _extract_from_notebook(fn: Any, nb_path: str) -> Optional[str]:
            """Parse a .ipynb file and extract the source for fn by name."""
            import json, ast as _ast

            try:
                with open(nb_path) as _f:
                    nb = json.load(_f)
                for cell in nb.get("cells", []):
                    if cell.get("cell_type") != "code":
                        continue
                    cell_src = "".join(cell.get("source", []))
                    try:
                        tree = _ast.parse(cell_src)
                    except SyntaxError:
                        continue
                    for node in _ast.walk(tree):
                        if (
                            isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef))
                            and node.name == fn.__name__
                        ):
                            cell_lines = cell_src.splitlines(keepends=True)
                            func_src = "".join(
                                cell_lines[node.lineno - 1 : node.end_lineno]
                            )
                            return textwrap.dedent(func_src).strip()
            except Exception:
                pass
            return None

        def _classify(fn: Any):
            mod = getattr(fn, "__module__", "") or ""
            if mod == "dynamicalnodes.ros2py_py2ros":
                return ("ros2py", fn.__name__)
            # Only importable if genuinely accessible as a top-level attribute
            # (rules out doctest / REPL / closure functions that carry a module name).
            if (
                mod
                and mod != "__main__"
                and not mod.startswith("<")
                and not mod.startswith("__")
            ):
                try:
                    m = importlib.import_module(mod)
                    if getattr(m, fn.__name__, None) is fn:
                        return ("module", mod, fn.__name__)
                except ImportError:
                    pass
            # Try inspect.getsource and validate the result is actually the right
            # function.  In VS Code's Jupyter extension co_filename is set to the
            # .ipynb path, so getsource reads the notebook JSON and returns '{'.
            co_filename = getattr(getattr(fn, "__code__", None), "co_filename", "")
            src = None
            try:
                raw = textwrap.dedent(inspect.getsource(fn)).strip()
                if raw.startswith(f"def {fn.__name__}") or raw.startswith(
                    f"async def {fn.__name__}"
                ):
                    src = raw
            except OSError:
                pass
            if src is None and co_filename.endswith(".ipynb"):
                src = _extract_from_notebook(fn, co_filename)
            if src is not None:
                return ("inline", src)
            raise OSError(
                f"Cannot retrieve source for {fn.__name__!r} "
                f"(module={mod!r}, co_filename={co_filename!r}). "
                f"Define it in a .py file or pass it via deps=."
            )

        def _ref_name(fn: Any, cls) -> str:
            if cls[0] == "inline":
                return fn.__name__
            return cls[-1]

        def _msg_module(msg_type: type) -> str:
            module = msg_type.__module__
            # ROS2 stores private submodule in __module__ (e.g. std_msgs.msg._float64);
            # must import from the public path (std_msgs.msg).
            if "._" in module:
                parent = module.rsplit(".", 1)[0]
                try:
                    m = importlib.import_module(parent)
                    if getattr(m, msg_type.__name__, None) is msg_type:
                        return parent
                except ImportError:
                    pass
            return module

        # ── validate ──────────────────────────────────────────────────────────

        if not self._subs and self._timer_hz is None and self._pubs_cfg:
            raise ValueError(
                "Cannot write a node with no subscriptions and no timer_hz — "
                "the generated node would never step.  Add timer_hz or subscribes_to."
            )

        ds = self._dynamical_system
        _check_lambda(ds.f, "DynamicalSystem.f")
        _check_lambda(ds.h, "DynamicalSystem.h")
        for _, _, ros2py, arg, _, _, _ in self._subs:
            _check_lambda(ros2py, f"ros2py for '{arg}'")
        for _, _, py2ros, key in self._pubs_cfg:
            _check_lambda(py2ros, f"py2ros for key={key!r}")

        _sub_noise: Dict[str, float] = dict(sub_noise or {})
        _pub_noise: Dict[str, float] = dict(pub_noise or {})
        _valid_sub_topics = {t for t, *_ in self._subs}
        _valid_pub_topics = {t for t, *_ in self._pubs_cfg}
        for t in _sub_noise:
            if t not in _valid_sub_topics:
                raise ValueError(f"sub_noise topic {t!r} not in subscribes_to")
        for t in _pub_noise:
            if t not in _valid_pub_topics:
                raise ValueError(f"pub_noise topic {t!r} not in publishes_to")

        # ── classify all functions ─────────────────────────────────────────────

        f_cls = _classify(ds.f) if ds.f is not None else None
        h_cls = _classify(ds.h)

        # subs: [(topic, msg_type, ros2py, cls, arg, stale, buf, use_msg_ts), ...]
        subs = []
        for topic, msg_type, ros2py, arg, stale, buf, use_msg_ts in self._subs:
            subs.append(
                (
                    topic,
                    msg_type,
                    ros2py,
                    _classify(ros2py),
                    arg,
                    stale,
                    buf,
                    use_msg_ts,
                )
            )

        # pubs: [(topic, msg_type, py2ros, cls, key, ident), ...]
        pubs = []
        for topic, msg_type, py2ros, key in self._pubs_cfg:
            pubs.append(
                (topic, msg_type, py2ros, _classify(py2ros), key, _ident(topic))
            )

        # ── gather imports ────────────────────────────────────────────────────

        msg_imports: Dict[str, List[str]] = {}
        for _, msg_type, _, _, _, _, _, _ in subs:
            mod = _msg_module(msg_type)
            msg_imports.setdefault(mod, [])
            if msg_type.__name__ not in msg_imports[mod]:
                msg_imports[mod].append(msg_type.__name__)
        for _, msg_type, _, _, _, _ in pubs:
            mod = _msg_module(msg_type)
            msg_imports.setdefault(mod, [])
            if msg_type.__name__ not in msg_imports[mod]:
                msg_imports[mod].append(msg_type.__name__)

        ros2py_names: List[str] = []
        for cls in (
            [f_cls, h_cls]
            + [c for _, _, _, c, _, _, _, _ in subs]
            + [c for _, _, _, c, _, _ in pubs]
        ):
            if cls is not None and cls[0] == "ros2py" and cls[1] not in ros2py_names:
                ros2py_names.append(cls[1])

        module_imports: Dict[str, List[str]] = {}
        for cls in (
            [f_cls, h_cls]
            + [c for _, _, _, c, _, _, _, _ in subs]
            + [c for _, _, _, c, _, _ in pubs]
        ):
            if cls is not None and cls[0] == "module":
                _, mod, name = cls
                module_imports.setdefault(mod, [])
                if name not in module_imports[mod]:
                    module_imports[mod].append(name)

        # Inline sources: ordered, deduplicated (deps → f → h → converters)
        inline_srcs: List[str] = []
        seen: set = set()

        def _add_inline(cls) -> None:
            if cls is None or cls[0] != "inline":
                return
            src = cls[1]
            if src not in seen:
                seen.add(src)
                inline_srcs.append(src)

        for dep in deps or []:
            _check_lambda(dep, f"deps function {getattr(dep, '__name__', '?')!r}")
            _add_inline(_classify(dep))
        _add_inline(f_cls)
        _add_inline(h_cls)
        for _, _, _, cls, _, _, _, _ in subs:
            _add_inline(cls)
        for _, _, _, cls, _, _ in pubs:
            _add_inline(cls)

        # ── line builder ──────────────────────────────────────────────────────

        L: List[str] = []

        def ln(*lines: str) -> None:
            L.extend(lines)

        def blank() -> None:
            L.append("")

        def rule(title: str = "") -> None:
            bar = "# " + "─" * 70
            L.append(bar)
            if title:
                L.append(f"# {title}")
                L.append(bar)

        # ── header ────────────────────────────────────────────────────────────

        cls_name = _class_name(node_name)

        from pathlib import Path as _Path

        ln("#!/usr/bin/env python3")
        ln('"""')
        ln(
            f"{node_name} — generated by dynamicalnodes.ROSNode.write_ROSNode_to_rclpy()."
        )
        ln("")
        ln(f"Run:")
        ln(f"    python3 {_Path(path).name}")
        ln('"""')
        blank()

        # ── imports ───────────────────────────────────────────────────────────

        rule("Imports")
        blank()
        ln("from collections import deque")
        ln("import numpy as np")
        blank()
        ln("import rclpy")
        ln("from rclpy.node import Node")
        ln("from rclpy.executors import SingleThreadedExecutor")
        ln("from rclpy.callback_groups import ReentrantCallbackGroup")
        ln("from rclpy.qos import QoSProfile, QoSHistoryPolicy, QoSReliabilityPolicy")
        blank()
        for mod, names in sorted(msg_imports.items()):
            ln(f"from {mod} import {', '.join(sorted(names))}")
        blank()
        ln("from dynamicalnodes import DynamicalSystem")
        if ros2py_names:
            ln(f"from dynamicalnodes.ros2py_py2ros import {', '.join(ros2py_names)}")
        for mod, names in sorted(module_imports.items()):
            ln(f"from {mod} import {', '.join(sorted(names))}")
        blank()
        blank()

        # ── inline functions ──────────────────────────────────────────────────

        if inline_srcs:
            rule("Functions — inlined from source")
            blank()
            for src in inline_srcs:
                ln(src)
                blank()
                blank()

        # ── QoS ───────────────────────────────────────────────────────────────

        rule("QoS — tune history / depth / reliability to match your transport")
        blank()
        ln("QOS = QoSProfile(")
        ln("    history=QoSHistoryPolicy.KEEP_LAST,")
        ln("    depth=10,")
        ln("    reliability=QoSReliabilityPolicy.RELIABLE,")
        ln(")")
        blank()
        blank()

        # ── Node class ────────────────────────────────────────────────────────

        # Collect type annotations for subscription args from f and h signatures.
        def _fmt_ann(ann) -> str:
            if hasattr(ann, "__name__"):
                return ann.__name__
            # strip leading module paths: numpy.ndarray[...] → ndarray[...]
            return re.sub(r"(?:\w+\.)+(\w+)", r"\1", str(ann))

        arg_annotations: Dict[str, str] = {}
        for _fn in filter(None, [ds.f, ds.h]):
            try:
                for pname, param in inspect.signature(_fn).parameters.items():
                    if (
                        param.annotation is not inspect.Parameter.empty
                        and pname not in arg_annotations
                    ):
                        arg_annotations[pname] = _fmt_ann(param.annotation)
            except (ValueError, TypeError):
                pass

        ln(f"class {cls_name}(Node):")
        blank()
        ln('    """')
        _initial = dict(initial_inputs or {})
        if subs:
            ln("    Subscribes to:")
            for (
                topic,
                msg_type,
                ros2py,
                ros2py_cls,
                arg,
                stale,
                buf,
                use_msg_ts,
            ) in subs:
                ann = arg_annotations.get(arg, "")
                arg_str = f"{arg}: {ann}" if ann else arg
                meta = [_ref_name(ros2py, ros2py_cls), f"buffer={buf}"]
                if stale is not None:
                    meta.append(f"stale_after={stale}s")
                if use_msg_ts:
                    meta.append("use_msg_timestamp=True")
                if arg in _initial:
                    meta.append(f"initial={_repr_value(_initial[arg])}")
                ln(
                    f"        {topic}  ({msg_type.__name__})  →  {arg_str}  [{', '.join(meta)}]"
                )
        if pubs:
            ln("    Publishes to:")
            for topic, msg_type, py2ros, py2ros_cls, key, _ in pubs:
                key_str = f", key={key!r}" if key else ""
                ln(
                    f"        {topic}  ({msg_type.__name__})  [{_ref_name(py2ros, py2ros_cls)}{key_str}]"
                )
        ln("")
        if self._timer_hz is not None:
            ln(f"    step trigger: timer at {self._timer_hz} Hz")
        else:
            ln("    step trigger: event-driven (fires on each subscription callback)")
        if subs:
            sync_desc = (
                "step only when every subscription has a fresh value"
                if self._sync_mode == "all"
                else "step when any subscription receives a fresh value"
            )
            ln(f"    sync_mode={self._sync_mode!r}: {sync_desc}.")
        _dynamic = dict(dynamic_params or {})
        if _dynamic:
            ln("")
            ln("    Dynamic params (ros2 param set /" + node_name + " <name> <value>):")
            for name, default in _dynamic.items():
                ln(f"        {name}: {_repr_value(default)}")
        ln('    """')
        blank()

        ln("    def __init__(self) -> None:")
        ln(f'        super().__init__("{node_name}")')
        ln("        self._cb_group = ReentrantCallbackGroup()")
        blank()

        f_ref = f"f={_ref_name(ds.f, f_cls)}" if ds.f is not None else None
        h_ref = f"h={_ref_name(ds.h, h_cls)}"
        ds_args = ", ".join(filter(None, [f_ref, h_ref]))
        ln(f"        self._system = DynamicalSystem({ds_args})")

        if initial_state is not None:
            ln(f"        self._state = {_repr_value(initial_state)}  # initial state")
        else:
            ln(
                "        self._state = None  # initial state — set before deploying if stateful"
            )

        ln("        self._t0 = self.get_clock().now()  # wall-clock reference for 'tk'")

        blank()
        _static = dict(static_params or {})
        if _static:
            ln(
                f"        self._static_params: dict = {_repr_value(_static)}  # static params"
            )
        else:
            ln(
                "        self._static_params: dict = {}  # static params — add fixed kwargs here, e.g. {'dt': 0.1}"
            )
        if _dynamic:
            blank()
            ln("        # ── Dynamic params " + "─" * 51)
            ln(
                "        # Readable/writable at runtime: ros2 param set /"
                + node_name
                + " <name> <value>"
            )
            for name, default in _dynamic.items():
                ln(f"        self.declare_parameter({name!r}, {_repr_value(default)})")

        if subs:
            blank()
            ln("        # ── Subscription buffers " + "─" * 47)
            for _, _, _, _, arg, _, buf, _ in subs:
                ln(f"        self._{arg}_buf: deque = deque(maxlen={buf})")

            blank()
            ln("        # ── Subscriptions " + "─" * 52)
            for topic, msg_type, _, _, arg, _, _, _ in subs:
                ln(f"        self._{_ident(topic)}_sub = self.create_subscription(")
                ln(f"            {msg_type.__name__}, {topic!r},")
                ln(f"            self._{arg}_cb, QOS,")
                ln(f"            callback_group=self._cb_group,")
                ln(f"        )")

        if pubs:
            blank()
            ln("        # ── Publishers " + "─" * 56)
            for topic, msg_type, _, _, _, ident in pubs:
                ln(f"        self._pub_{ident} = self.create_publisher(")
                ln(f"            {msg_type.__name__}, {topic!r}, QOS,")
                ln(f"        )")

        if self._timer_hz is not None:
            blank()
            ln("        # ── Timer " + "─" * 60)
            period = 1.0 / self._timer_hz
            ln(f"        self._timer = self.create_timer(")
            ln(f"            {period},  # {self._timer_hz} Hz")
            ln(f"            self._run_step,")
            ln(f"            callback_group=self._cb_group,")
            ln(f"        )")

        blank()
        ln(f'        self.get_logger().info("{node_name} started")')

        # Subscription callbacks
        if subs:
            blank()
            ln("    # " + "─" * 68)
            ln("    # Subscription callbacks")
            ln("    # " + "─" * 68)
            ln(
                "    # Each callback converts the incoming message to NumPy, stores it with an"
            )
            ln(
                "    # arrival timestamp, then attempts a control step. The (time, value) tuple"
            )
            ln(
                "    # enables the staleness check in _fresh(). _run_step() proceeds only when"
            )
            ln("    # sync_mode conditions are satisfied.")
        for topic, msg_type, ros2py, cls, arg, _, _, use_msg_ts in subs:
            ros2py_name = _ref_name(ros2py, cls)
            blank()
            ln(f"    def _{arg}_cb(self, msg: {msg_type.__name__}) -> None:")
            ln(
                f"        arr = np.asarray({ros2py_name}(msg), dtype=float)  # ROS msg → NumPy"
            )
            if topic in _sub_noise:
                std = _sub_noise[topic]
                ln(
                    f"        arr = arr + np.random.normal(0.0, {std!r}, arr.shape)  # noise std={std}"
                )
            if use_msg_ts:
                ln(
                    f"        ts = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9"
                )
            else:
                ln(f"        ts = self.get_clock().now().nanoseconds * 1e-9")
            ln(f"        self._{arg}_buf.append((ts, arr))")
            if self._timer_hz is None:
                ln(f"        self._run_step()")

        # _fresh
        blank()
        ln("    @staticmethod")
        ln("    def _fresh(buf: deque, stale_after, now_ts: float):")
        ln(
            '        """Newest buffered value if its timestamp is within stale_after seconds of now_ts, else None."""'
        )
        ln("        if not buf:")
        ln("            return None")
        ln("        ts, val = buf[-1]")
        ln("        if stale_after is not None and (now_ts - ts) > stale_after:")
        ln("            return None")
        ln("        return val")

        # _run_step
        blank()
        ln("    # " + "─" * 68)
        ln("    # Control step")
        ln("    # " + "─" * 68)
        ln("    # Builds kwargs from static params, dynamic params, fresh subscription")
        ln("    # values, and current state, then calls DynamicalSystem.step() and")
        ln("    # publishes. Skipped entirely when sync_mode conditions are not met.")
        blank()
        ln("    def _run_step(self) -> None:")
        ln("        _now = self.get_clock().now()")
        ln(
            "        now_ts: float = _now.nanoseconds * 1e-9  # ROS clock, seconds since epoch"
        )
        ln(
            "        tk: float = (_now - self._t0).nanoseconds * 1e-9  # seconds since node started"
        )

        if subs:
            blank()
            ln("        # Gather fresh inputs")
            for _, _, _, _, arg, stale, _, _ in subs:
                ln(f"        {arg} = self._fresh(self._{arg}_buf, {stale!r}, now_ts)")
            cold_start_args = [
                arg for _, _, _, _, arg, _, _, _ in subs if arg in _initial
            ]
            if cold_start_args:
                blank()
                ln(
                    "        # Cold-start fallbacks — used only before first message arrives"
                )
                for arg in cold_start_args:
                    ln(f"        if {arg} is None and not self._{arg}_buf:")
                    ln(
                        f"            {arg} = {_repr_value(_initial[arg])}  # initial input"
                    )

            blank()
            ln(f"        # sync_mode={self._sync_mode!r}")
            if self._sync_mode == "all":
                cond = " or ".join(f"{a} is None" for _, _, _, _, a, _, _, _ in subs)
                ln(f"        if {cond}:")
                ln("            return  # not all inputs are fresh — skip this tick")
            else:
                cond = " and ".join(f"{a} is None" for _, _, _, _, a, _, _, _ in subs)
                ln(f"        if {cond}:")
                ln("            return  # all inputs are stale — skip this tick")

        blank()
        ln('        kwargs: dict = {"tk": tk, **self._static_params}')
        for name in _dynamic:
            ln(f'        kwargs["{name}"] = self.get_parameter("{name}").value')
        for _, _, _, _, arg, _, _, _ in subs:
            ln(f"        if {arg} is not None:")
            ln(f'            kwargs["{arg}"] = {arg}')
        if self._state_key is not None:
            ln(f"        if self._state is not None:")
            ln(f'            kwargs["{self._state_key}"] = self._state')

        blank()
        ln("        result = self._system.step(**kwargs)")
        ln("        if self._system.f is not None:")
        ln("            self._state, yk = result  # stateful: (next_state, output)")
        ln("        else:")
        ln("            yk = result               # stateless: output only")

        if pubs:
            blank()
            for topic, msg_type, py2ros, cls, key, ident in pubs:
                py2ros_name = _ref_name(py2ros, cls)
                if key is not None:
                    ln(f"        if isinstance(yk, dict) and {key!r} in yk:")
                    ln(
                        f"            _arr = np.asarray(yk[{key!r}], dtype=float).ravel()"
                    )
                    if topic in _pub_noise:
                        std = _pub_noise[topic]
                        ln(
                            f"            _arr = _arr + np.random.normal(0.0, {std!r}, _arr.shape)  # noise std={std}"
                        )
                    ln(f"            msg = {py2ros_name}(_arr)")
                    ln(f"            if hasattr(msg, 'header'):")
                    ln(
                        f"                msg.header.stamp = self.get_clock().now().to_msg()"
                    )
                    ln(f"            self._pub_{ident}.publish(msg)")
                else:
                    ln(f"        _arr = np.asarray(yk, dtype=float).ravel()")
                    if topic in _pub_noise:
                        std = _pub_noise[topic]
                        ln(
                            f"        _arr = _arr + np.random.normal(0.0, {std!r}, _arr.shape)  # noise std={std}"
                        )
                    ln(f"        msg = {py2ros_name}(_arr)")
                    ln(f"        if hasattr(msg, 'header'):")
                    ln(
                        f"            msg.header.stamp = self.get_clock().now().to_msg()"
                    )
                    ln(f"        self._pub_{ident}.publish(msg)")

        # ── main ──────────────────────────────────────────────────────────────

        blank()
        blank()
        rule("Entry point")
        blank()
        ln("def main() -> None:")
        ln("    rclpy.init()")
        ln(f"    node = {cls_name}()")
        ln("    executor = SingleThreadedExecutor()")
        ln("    executor.add_node(node)")
        ln("    try:")
        ln("        executor.spin()")
        ln("    except KeyboardInterrupt:")
        ln("        pass")
        ln("    finally:")
        ln("        node.destroy_node()")
        ln("        rclpy.shutdown()")
        blank()
        blank()
        ln('if __name__ == "__main__":')
        ln("    main()")
        ln("")

        import ast as _ast

        content = "\n".join(L)
        try:
            _ast.parse(content)
        except SyntaxError as e:
            raise SyntaxError(
                f"write_ROSNode_to_rclpy generated invalid Python at line {e.lineno}: {e.msg}\n"
                f"  {e.text}\n"
                f"This is a bug in the generator — please report it."
            ) from e
        Path(path).write_text(content)
