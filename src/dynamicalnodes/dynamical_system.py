"""
A discrete-time dynamical system (DTDS) is represented as a pair of functions,
``(f, h)``, following the definition in Mangat et al., *dynamicalnodes: From
Theory to Python to ROS*::

    x_{k+1} = f(x_k, u_k, theta)
    y_k     = h(x_k, u_k, theta)

``f`` is the evolution function that propagates the state forward one step;
``h`` is the measurement (or output) function that computes an observation
from the current state. Either function may be omitted -- denoted ``*`` in
the paper, ``None`` here -- giving three cases:

- ``(f, *)`` -- no output function.
- ``(*, h)`` -- stateless, e.g. a signal generator.
- ``(f, h)`` -- both state evolution and output are defined.

Function signatures are unconstrained in name, type, and number of
parameters. ``DynamicalSystem.eval`` binds keyword arguments to each
function's signature by name, so the same keyword argument (e.g. a shared
state or parameter) can be passed to both ``f`` and ``h``.
"""

import inspect
from typing import Any, Callable, Dict, Optional, Tuple


class DynamicalSystem:
    """
    A discrete-time dynamical system with (optional) evolution and
    (optional) measurement functions.

    Parameters
    ----------
    f : Callable, optional
        Evolution function ``f(x_k, u_k, theta) -> x_{k+1}``. ``None`` if
        the system has no state transition, i.e. ``(*, h)``.
    h : Callable, optional
        Measurement function ``h(x_k, u_k, theta) -> y_k``. ``None`` if
        the system has no output, i.e. ``(f, *)``.

    Examples
    --------
    A stateful system with both an evolution and a measurement function --
    a car whose state is ``(displacement, velocity)``, measured via its
    speed:

    >>> def fcar(xk, uk, theta_car):
    ...     d, v = xk
    ...     m, b, dt = theta_car
    ...     return (d + dt * v, v + dt * (uk - b * v) / m)
    >>> def hcar(xk):
    ...     _, v = xk
    ...     return abs(v)
    >>> car = DynamicalSystem(f=fcar, h=hcar)
    >>> x_next, y = car.eval(xk=(20.0, 0.0), uk=4.0, theta_car=(2.0, 0.0, 1.0))
    >>> x_next
    (20.0, 2.0)
    >>> y
    0.0

    A stateless system, e.g. a signal generator -- ``(*, h)``:

    >>> def h_ref(tk, A=1.0):
    ...     return A if tk >= 1.0 else 0.0
    >>> ref = DynamicalSystem(h=h_ref)
    >>> ref.eval(tk=0.0)
    (None, 0.0)
    >>> ref.eval(tk=2.0)
    (None, 1.0)

    A system with no output function -- ``(f, *)``:

    >>> def f_counter(xk):
    ...     return xk + 1
    >>> counter = DynamicalSystem(f=f_counter)
    >>> counter.eval(xk=5)
    (6, None)
    """

    def __init__(
        self,
        *,
        f: Optional[Callable] = None,
        h: Optional[Callable] = None,
    ) -> None:
        """
        Parameters
        ----------
        f : Callable, optional
            Evolution function ``f(x_k, u_k, theta) -> x_{k+1}``. Signature
            typing is not enforced. ``None`` if the system is stateless.
        h : Callable, optional
            Measurement function ``h(x_k, u_k, theta) -> y_k``. Signature
            typing is not enforced. ``None`` if the system has no output.
        """
        self._f = f
        self._h = h

    @property
    def f(self) -> Optional[Callable]:
        """Evolution function f(x_k, u_k, theta) -> x_{k+1}, or None if the system is stateless."""
        return self._f

    @f.setter
    def f(self, f: Optional[Callable]) -> None:
        self._f = f

    @property
    def h(self) -> Optional[Callable]:
        """Measurement function h(x_k, u_k, theta) -> y_k, or None if the system has no output."""
        return self._h

    @h.setter
    def h(self, h: Optional[Callable]) -> None:
        self._h = h

    def eval(self, **kwargs) -> Tuple[Optional[Any], Optional[Any]]:
        """
        Evaluate the system for one discrete time step.

        Keyword arguments are lexically bound by name to whichever of ``f``
        and/or ``h`` declare them in their signature (see
        ``_bind_and_call``), so the same keyword argument can be shared by
        both functions.

        Returns
        -------
        Tuple[Optional[Any], Optional[Any]]
            - ``(None, y_k)`` for a stateless system, ``(*, h)``.
            - ``(x_{k+1}, None)`` for a system with no output, ``(f, *)``.
            - ``(x_{k+1}, y_k)`` for a fully specified system, ``(f, h)``.

        Notes
        -----
        ``h`` is evaluated on the same (pre-update) state passed in via
        keyword arguments, not on the value returned by ``f``, so the
        returned observation is one step behind the returned state. In a
        simulation loop, use the returned ``x_{k+1}`` directly if you need
        the post-update state.

        Raises
        ------
        ValueError
            If neither ``f`` nor ``h`` is defined.

        Examples
        --------
        See the class docstring for worked examples covering all three
        cases.

        >>> empty = DynamicalSystem()
        >>> empty.eval()
        Traceback (most recent call last):
            ...
        ValueError: Nothing to evaluate; no f or h functions!
        """

        def _bind_and_call(
            func: Callable[..., Any],
            **kwargs: Any,
        ) -> Any:
            """
            Call `func` with only the keyword arguments it declares.

            Inspects `func`'s signature and passes only the entries of
            `kwargs` matching its declared parameter names; if `func`
            accepts `**kwargs`, the remaining pool is passed through too.
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

        if self.f is None and self.h:
            return (None, _bind_and_call(self.h, **kwargs))

        elif self.f and self.h is None:
            return (_bind_and_call(self.f, **kwargs), None)

        elif self.f and self.h:
            return (
                _bind_and_call(self.f, **kwargs),
                _bind_and_call(self.h, **kwargs),
            )

        else:
            raise ValueError("Nothing to evaluate; no f or h functions!")
