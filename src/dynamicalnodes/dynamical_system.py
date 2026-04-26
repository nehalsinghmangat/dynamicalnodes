"""
Core abstraction for modeling dynamical systems in dynamicalnodes.

A dynamical system is defined by two functions:
- f: State transition function (optional) - computes next state
- h: Observation function (required) - computes output from state

This abstraction allows any control system component (plants, controllers,
observers, reference signals) to be modeled uniformly and composed together.
"""

import inspect
from typing import Any, Callable, Dict, Optional


class DynamicalSystem:
    """
    A discrete-time dynamical system with state transition and observation functions.

    This class provides a unified abstraction for modeling control system components.
    Each component is defined by:

    - **f(x_k, u_k, ...) -> x_{k+1}**: State transition function (optional)
    - **h(x_k, u_k, ...) -> y_k**: Observation/output function (required)

    The `step()` method executes one timestep: it calls f to update state,
    then calls h to compute the output.

    Parameters
    ----------
    f : Callable, optional
        State transition function. Signature: f(x_k, u_k, ...) -> x_{k+1}
        If None, the system is stateless (e.g., a reference signal generator).
    h : Callable
        Observation function. Signature: h(x_k, u_k, ...) -> y_k
        This function computes the system output.

    Examples
    --------
    Stateless reference signal (step function):

    >>> def h_ref(tk, params):
    ...     u0, t_step = params
    ...     return u0 if tk >= t_step else 0.0
    >>> ref_signal = DynamicalSystem(h=h_ref)
    >>> ref_signal.step(tk=0.0, params=(100, 15))  # Before step time
    0.0
    >>> ref_signal.step(tk=20.0, params=(100, 15))  # After step time
    100

    Stateful plant (discrete-time integrator):

    >>> def f_plant(x_k, u_k, dt):
    ...     return x_k + u_k * dt
    >>> def h_plant(x_k, u_k, dt):
    ...     return x_k
    >>> plant = DynamicalSystem(f=f_plant, h=h_plant)
    >>> x_next, y = plant.step(x_k=0.0, u_k=1.0, dt=0.1)
    >>> x_next
    0.1

    Notes
    -----
    The `_smart_call` mechanism allows flexible parameter binding. Functions
    only receive the parameters they declare in their signature, enabling
    components with different interfaces to be composed together.

    See Also
    --------
    ROSNode : Wraps a DynamicalSystem as a ROS2 node for deployment.
    """

    def __init__(
        self,
        *,
        f: Optional[Callable] = None,
        h: Callable,
    ) -> None:
        """
        Initialize a DynamicalSystem with state transition and observation functions.

        Parameters
        ----------
        f : Callable, optional
            State transition function: f(x_k, u_k, ...) -> x_{k+1}
        h : Callable
            Observation function: h(x_k, u_k, ...) -> y_k
        """
        self._f = f
        self._h = h

    @property
    def f(self) -> Optional[Callable]:
        """State transition function f(x_k, u_k, ...) -> x_{k+1}, or None if stateless."""
        return self._f

    @f.setter
    def f(self, f: Optional[Callable]) -> None:
        self._f = f

    @property
    def h(self) -> Callable:
        """Observation function h(x_k, u_k, ...) -> y_k."""
        return self._h

    @h.setter
    def h(self, h: Callable) -> None:
        self._h = h

    @staticmethod
    def _smart_call(
        func: Callable[..., Any],
        **kwargs: Any,
    ) -> Any:
        """
        Call a function with smart parameter binding by name.

        This method inspects the function signature and passes only the
        parameters that the function declares. This enables flexible
        composition of components with different interfaces.

        Parameters
        ----------
        func : Callable
            The function to call.
        **kwargs : Any
            Keyword arguments pool. Only arguments matching the function's
            declared parameters are passed.

        Returns
        -------
        Any
            The return value of the function.

        Notes
        -----
        If the function has a **kwargs parameter, all remaining kwargs
        from the pool are passed through.

        Examples
        --------
        Functions receive only the parameters they declare:

        >>> def needs_time(tk, gain): return tk * gain
        >>> def needs_state(xk, gain): return (xk, gain)
        >>> def needs_both(tk, xk, gain): return (tk, xk, gain)

        >>> DynamicalSystem._smart_call(needs_time, tk=1.0, xk=[0, 0], gain=2.0)
        2.0
        >>> DynamicalSystem._smart_call(needs_state, tk=1.0, xk=[5, 5], gain=2.0)
        ([5, 5], 2.0)
        >>> DynamicalSystem._smart_call(needs_both, tk=1.0, xk='state', gain=2.0)
        (1.0, 'state', 2.0)
        """
        sig = inspect.signature(func)
        pool: Dict[str, Any] = dict(kwargs)

        # Filter: only pass arguments the function declares
        call_kwargs: Dict[str, Any] = {}
        for name, p in sig.parameters.items():
            if p.kind in (
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
                inspect.Parameter.KEYWORD_ONLY,
            ):
                if name in pool:
                    call_kwargs[name] = pool.pop(name)

        # Pass remaining kwargs if function has **kwargs
        if any(
            p.kind is inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values()
        ):
            call_kwargs.update(pool)

        return func(**call_kwargs)

    def step(self, **kwargs: Any) -> Any:
        """
        Execute one timestep of the dynamical system.

        This method calls the state transition function f (if defined) and
        the observation function h with the provided keyword arguments.

        Parameters
        ----------
        **kwargs : Any
            Keyword arguments passed to f and h. Each function receives
            only the kwargs it declares in its signature via `_smart_call`.

        Returns
        -------
        Any
            If f is None (stateless system):
                Returns y_k = h(...)
            If f is defined (stateful system):
                Returns (x_{k+1}, y_k) = (f(...), h(...))

        Examples
        --------
        Stateless system (no f):

        >>> def h(tk): return tk * 2
        >>> sys = DynamicalSystem(h=h)
        >>> sys.step(tk=5.0)
        10.0

        Stateful system (with f):

        >>> def f(x, u): return x + u
        >>> def h(x, u): return x
        >>> sys = DynamicalSystem(f=f, h=h)
        >>> x_next, y = sys.step(x=0.0, u=1.0)
        >>> x_next, y
        (1.0, 0.0)
        """
        if self.f is None:
            return self._smart_call(self.h, **kwargs)

        return (
            self._smart_call(self.f, **kwargs),
            self._smart_call(self.h, **kwargs),
        )
