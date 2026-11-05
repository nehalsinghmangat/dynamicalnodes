---
name: simulate-with-dynamicalsystem
description: Write a Python for-loop simulation of one or more dynamicalnodes DynamicalSystem objects, including closed-loop feedback (reference, controller, plant, observer). Use when the user wants to simulate, compose, or debug DynamicalSystem blocks, order the step() calls, initialize states and feedback inputs, store history, or plot results before moving to ROS.
---

# Simulate DynamicalSystem blocks in a for-loop

Prerequisite: each block already has `f`/`h` functions (see the `discretize-f-h` skill) wrapped as `DynamicalSystem(f=..., h=...)`. Background: tutorial sections "The `DynamicalSystem` Class (III-B)" and "Simulating the Discrete-Time Diagram" in `docs/source/tutorials/0_cruise_control/cruise_control_with_dynamicalnodes.ipynb`; rules for `step` in `CLAUDE.md`.

## Rules of the loop

- `block.step(**kwargs)` returns `(x_next, y)`. `y = h(x_k, ...)` is computed from the **pre-update** state; `x_next` is the state at `k+1`. Use `_` for the half you don't need (`_, rk = ref.step(...)` for `(*, h)`).
- Within iteration `k`, call blocks **in signal-flow order**, each with its step-`k` inputs, and keep every `x_next` in a `*_next` variable. Assign all states forward **together at the end** (`ck, xk, ok = ck_next, xk_next, ok_next`). Overwriting a state mid-loop mixes time indices.
- A feedback edge (e.g. estimate → controller) closes a loop. Supply an **initial value** for the signal before iteration 0, and note that the value used at step `k` is the one produced at `k−1` (one-sample delay). That is the standard way to break an algebraic loop.
- Time: define `t_sim = np.arange(0, T, dt)`; pass `tk=tk` only to blocks that declare `tk`.
- Collect histories in lists (`r_hist`, `u_hist`, ...) and convert with `np.array(...)` to plot.

## Template

Reference → PID → plant, plant output fed back (verified runnable):

```python
import numpy as np
from dynamicalnodes import DynamicalSystem

def h_ref(tk, A=1.0, omega=0.1): return A * np.sin(omega * tk)          # (*, h)
def f_car(xk, uk, m=1500.0, b=50.0, dt=1.0): return xk + dt * (uk - b * xk) / m
def h_car(xk, sigma=0.0): return xk + np.random.normal(0.0, sigma)
def f_pid(ck, rk, yk, dt=1.0):                                           # ck = (e_prev, e_int)
    ek = rk - yk
    return (ek, ck[1] + ek * dt)
def h_pid(ck, rk, yk, KP=500.0, KI=30.0, KD=10.0, dt=1.0):
    ek = rk - yk
    return KP * ek + KI * ck[1] + KD * (ek - ck[0]) / dt

ref = DynamicalSystem(h=h_ref)
car = DynamicalSystem(f=f_car, h=h_car)
pid = DynamicalSystem(f=f_pid, h=h_pid)

dt = 1.0
t_sim = np.arange(0, 60, dt)
xk, ck = 0.0, (0.0, 0.0)          # initial states
yk = 0.0                          # initial feedback input: nothing has run yet
r_hist, u_hist, y_hist = [], [], []
for tk in t_sim:
    _, rk = ref.step(tk=tk, A=30.0, omega=np.pi / 60)
    ck_next, uk = pid.step(ck=ck, rk=rk, yk=yk, dt=dt)
    xk_next, yk = car.step(xk=xk, uk=uk, dt=dt, sigma=0.5)
    r_hist.append(rk); u_hist.append(uk); y_hist.append(yk)
    ck, xk = ck_next, xk_next
```

## Composition and estimators

- **Chains** need no glue: the output of one `step` is just the keyword of the next (`uk=uk`). Any block can ignore kwargs it doesn't declare.
- **Observers** (Kalman filter etc.): the tutorial's filter is in *prior form* `ok = (x̂_{k|k-1}, P_{k|k-1})`: `fkf` updates with `yk` first, then predicts with `uk`; `hkf(ok)` returns the prior estimate. Feed `float(xhat[0])` to a scalar controller. See "Linear Kalman Filter (IV-D)".
- **Optional inputs**: a block may take `uk=None`/`yk=None` and skip that half when absent. This is what lets it run with `sync_mode="any"` later.
- **Parameters** (`m`, `b`, `dt`, gains) go straight into `step(...)`; each block only receives the ones it declares.

## Common mistakes

- **Misspelled kwargs are silently ignored** (the default is used). If a parameter change has no effect, check the spelling.
- A required argument that nobody passes raises `TypeError`, not a helpful message. Check the names in the block signatures.
- Forgetting the initial feedback value (`NameError` at iteration 0) or initializing it with the wrong type.
- Reading `y` as if it were the *next* output: it is `h(x_k)`, the output of the state *before* the update. Use `x_next` for the post-update state.
- Vector vs scalar types: filter outputs are arrays (shape `(1,)`); cast with `float(...)` when a downstream block expects a float.
- Seeds: noise inside `h` makes two runs differ. Call `np.random.seed(...)` before each loop when comparing runs.
- Nothing here needs ROS. Don't import ROS message types until the `wrap-in-rosnode` step.

Next: `wrap-in-rosnode` (same loop on ROS types), then `deploy-rosnodes-to-rclpy`.
