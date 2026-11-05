---
name: discretize-f-h
description: Turn continuous-time dynamics (x' = f_c(x,u,θ), y = h_c(x,u,θ), or A/B/C matrices) into discrete-time f and h Python functions for a dynamicalnodes DynamicalSystem. Use when the user has an ODE, state-space model, or physics equations and needs x_{k+1} = f(x_k, u_k, ...) and y_k = h(x_k, ...), or asks about Euler, RK4, matrix exponential, zero-order hold, or choosing dt.
---

# Discretize continuous-time f and h

Goal: produce plain Python functions `f(xk, uk, ...) -> xk_next` and `h(xk, ...) -> yk` that a `DynamicalSystem` can wrap. Background: tutorial sections "Dynamical Systems (II-A)" (CTDS/DTDS) in `docs/source/tutorials/0_cruise_control/cruise_control_with_dynamicalnodes.ipynb`; semantics of `f`/`h`/`step` in `CLAUDE.md`.

## Steps

1. **Pin down the model.** Write down the state `x`, input `u`, parameters `θ`, and output `y`. Decide the time step `dt` (see below).
2. **Pick a scheme.**
   - *Linear, time-invariant* (`x' = A x + B u`): discretize **exactly** with a zero-order hold, `A_d = expm(A·dt)`, `B_d = A⁻¹(A_d − I)B` when `A` is invertible. When `A` may be singular, use one block exponential, `expm([[A, B],[0, 0]]·dt) = [[A_d, B_d],[0, I]]`.
   - *Nonlinear or time-varying*: use a one-step integrator. Forward Euler is the simplest (`x + dt·f_c`); RK4 is the usual upgrade. Both are only accurate and stable for small `dt`.
3. **Leave `h` alone.** The measurement function is algebraic, so there is nothing to discretize. Copy `h_c` over. Add noise as an optional parameter (`sigma=0.0` with `np.random.normal`) if the user wants a noisy sensor.
4. **Write the functions** following the conventions below.
5. **Validate** against `scipy.integrate.solve_ivp` with tight tolerances: max error should be ~1e-10 for the exact scheme and small for RK4/Euler. Fix `dt` or the scheme if it isn't.
6. **Wrap**: `sys = DynamicalSystem(f=f, h=h)`. Either may be omitted: `(f, *)`, `(*, h)`.

## Conventions

- First parameter of `f` is the state (`xk`), then inputs (`uk`), then parameters as keyword arguments with **defaults** (`dt`, `m`, `b`, ...). `step(**kwargs)` binds by name, so keep names consistent across blocks.
- `f` must return the same type and shape as `xk`. Use an `np.ndarray` for vector states, a `float` for scalars. Don't mutate `xk` in place.
- Declare time as `tk` only when `f`/`h` truly depend on it (it is the one reserved name; a generated node fills it with node-clock seconds).
- `h` sees the **pre-update** state: `y_k = h(x_k)`.
- Keep functions **self-contained**. If they will be deployed with `ROSNode.write_ROSNode_to_rclpy`, they must be named functions (no lambdas) that use no hidden globals. Define an RK4 `g(x)` *inside* `f`, or pass helpers via `deps=` later.
- Precompute `A_d`, `B_d` once and pass them as parameters if `f` will run at high rate; recomputing `expm` per call is fine for tutorials only.

## Example (mass-spring-damper, verified against `solve_ivp`)

```python
import numpy as np
from scipy.linalg import expm
from dynamicalnodes import DynamicalSystem

m, c, k = 1.0, 0.4, 2.0
A = np.array([[0.0, 1.0], [-k / m, -c / m]])
B = np.array([[0.0], [1.0 / m]])

def f_exact(xk, uk, dt=0.1, A=A, B=B):      # linear: exact ZOH
    n = A.shape[0]
    M = np.zeros((n + 1, n + 1))
    M[:n, :n], M[:n, n:] = A, B
    E = expm(M * dt)                         # [[Ad, Bd], [0, 1]]
    return E[:n, :n] @ xk + E[:n, n:] @ np.atleast_1d(uk)

def f_rk4(xk, uk, dt=0.1, m=1.0, c=0.4, k=2.0):   # nonlinear-ready: one RK4 step
    def g(x):                                # continuous-time f_c
        return np.array([x[1], (uk - c * x[1] - k * x[0]) / m])
    k1 = g(xk); k2 = g(xk + dt / 2 * k1)
    k3 = g(xk + dt / 2 * k2); k4 = g(xk + dt * k3)
    return xk + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)

def h(xk, sigma=0.0):                        # position measurement
    return xk[0] + np.random.normal(0.0, sigma)

osc = DynamicalSystem(f=f_exact, h=h)
x_next, y = osc.step(xk=np.array([1.0, 0.0]), uk=1.0, dt=0.1)
```

Measured error vs `solve_ivp` over 10 s at `dt = 0.1`: exact ≈ 5e-11, RK4 ≈ 6e-6.

## Common mistakes

- Wrong `dt` units or a `dt` mismatch between this model and a later ROS timer (see the `deploy-rosnodes-to-rclpy` skill).
- Inverting a singular `A` (e.g. a free integrator): use the block-matrix exponential.
- Returning a list or tuple from `f` when `xk` is an array (or vice versa).
- Misspelled parameter names in `step(...)` are **silently ignored** and the default is used, so test with non-default values.
- Euler with large `dt` on an oscillator gains energy: reduce `dt` or switch to RK4/exact.

Next: simulate it in a loop with the `simulate-with-dynamicalsystem` skill.
