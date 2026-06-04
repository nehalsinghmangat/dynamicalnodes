"""
A dynamical system is defined by two functions:

- f: State transition function (optional) - computes next state
- h: Output/observation function (required) - computes output from state

The dynamical system abstraction can model any control system componenent (e.g. plants, controllers, observers, signal generators, etc...) and enables their composition via the discrete-time diagram.
"""

import inspect
from typing import Any, Callable, Dict, Optional


class DynamicalSystem:
    """
    A discrete-time dynamical system with (optional) state transition and (required) output functions.

    Methods
    ----------
    ``step(**kwargs)``: Compute ``x_{k+1}, y_k = (f(*f_args, **f_kwargs), h(*h_args, **h_kwargs))``. For each keyword=value in ``**kwargs``, step binds the value to the keyword and then passes it to any function that declares that keyword as a parameter. See examples below.

    Examples
    --------

    Autonomous System with Parameters -- Exponential Growth

    (put math and background explanation here.)

    >>> def fexp(x_k):
    ...     return x_k dt
    >>> def hexp(x_k, u_k, dt):
    ...     return x_k
    >>> plant = DynamicalSystem(f=f_plant, h=h_plant)
    >>> x_next, y = plant.step(x_k=0.0, u_k=1.0, dt=0.1)
    >>> x_next
    0.1

    Non-autonomous System with control input and parameters  -- Car Dynamics

    (put math and background explanation here.)

    Signal Generator (stateless DTDS)

    (put math and background explanation here.)

    >>> def h_ref(tk, params):
    ...     u0, t_step = params
    ...     return u0 if tk >= t_step else 0.0
    >>> ref_signal = DynamicalSystem(h=h_ref)
    >>> ref_signal.step(tk=0.0, params=(100, 15))  # Before step time
    0.0
    >>> ref_signal.step(tk=20.0, params=(100, 15))  # After step time
    100

    Note: All functions have type hints in their signature. This is the modern (and much better) way of writing functions.

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
        Initialize a discrete-time DynamicalSystem with state transition and output functions.

        Parameters
        ----------
        f : Callable, optional
        State transition function.  Signature typing is not enforced, but must be of the form: f(*args,**kwargs) -> x_{k+1}
        If None, the system is stateless (e.g. a signal generator).

        Note:
        h : Callable
        Output function. Signature typing is not enforced, but must be of the form: h(*args,**kwargs) -> y_{k}
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
        parameters that the function declares.

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
        Compute ``x_{k+1}, y_k = (f(*f_args, **f_kwargs), h(*h_args, **h_kwargs))``. For each keyword=value in ``**kwargs``, step binds the value to the keyword and then passes it to any function that declares that keyword as a parameter. See examples below.

        Returns
        -------
        Any
        If f is None (stateless system):
            Returns y_k = h(...)
        If f is defined (stateful system):
            Returns (x_{k+1}, y_k) = (f(...), h(...))

        Examples
        --------

        Autonomous System with Parameters -- Exponential Growth

        (put math and background explanation here.)

        >>> def fexp(x_k):
        ...     return x_k dt
        >>> def hexp(x_k, u_k, dt):
        ...     return x_k
        >>> plant = DynamicalSystem(f=f_plant, h=h_plant)
        >>> x_next, y = plant.step(x_k=0.0, u_k=1.0, dt=0.1)
        >>> x_next
        0.1

        Non-autonomous System with control input and parameters  -- Car Dynamics

        (put math and background explanation here.)

        Signal Generator (stateless DTDS)

        (put math and background explanation here.)

        >>> def h_ref(tk, params):
        ...     u0, t_step = params
        ...     return u0 if tk >= t_step else 0.0
        >>> ref_signal = DynamicalSystem(h=h_ref)
        >>> ref_signal.step(tk=0.0, params=(100, 15))  # Before step time
        0.0
        >>> ref_signal.step(tk=20.0, params=(100, 15))  # After step time
        100

        Note: All functions have type hints in their signature. This is the modern (and much better) way of writing functions.
        """
        if self.f is None:
            return self._smart_call(self.h, **kwargs)

        return (
            self._smart_call(self.f, **kwargs),
            self._smart_call(self.h, **kwargs),
        )
