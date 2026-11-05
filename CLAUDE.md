# CLAUDE.md

Guidance for Claude Code (claude.ai/code) working in this repository, and for any Claude instance helping a person learn or use the package. If you are helping a user, start with **Helping users** below; the rest is for people changing the repo.

## Project Overview

**dynamicalnodes** (v0.2.1, Python >=3.12, MIT) is a Python framework that bridges control-systems theory and ROS2. Pipeline: **Theory → Python → ROS2 → Hardware**.

1. Cast the system as a discrete-time diagram; derive an `(f, h)` pair per block.
2. Implement each `f`/`h` as a plain Python function; wrap in a `DynamicalSystem`; simulate with an ordinary `for` loop.
3. Wrap each block in a `ROSNode`, test the loop again (still pure Python), then `write_ROSNode_to_rclpy()` to emit a standalone rclpy file per block.
4. Run the generated nodes on a ROS2 graph (simulation or hardware).

The whole public API is two classes and three methods:

```
dynamicalnodes
├── DynamicalSystem                # class
│   └── .step()
├── ROSNode                        # class
│   ├── .step()
│   └── .write_ROSNode_to_rclpy()
└── ros2py_py2ros                  # accessory module (needs a live ROS2 install)
```

Docs: https://nehalsinghmangat.github.io/dynamicalnodes (API pages at `/api/<module>.html#dynamicalnodes.<module>.<Name>`).

## Core Architecture

All source is under `src/dynamicalnodes/` (flat layout):

1. **`dynamical_system.py`** — `DynamicalSystem(f=None, h=None)`
   - `f(x_k, u_k, θ) → x_{k+1}`, `h(x_k, u_k, θ) → y_k`; either may be `None`: `(f, *)`, `(*, h)`, `(f, h)`.
   - `step(**kwargs)` returns `(x_next, y)` with `None` for an unset half; `ValueError` if both are unset.
   - `_bind_and_call()` passes each function only the kwargs it declares in its signature, binding **by name**. This is what makes blocks with different signatures compose.
   - With both `f` and `h`, both get the same kwargs and **`h` sees the pre-update state** (`y_k = h(x_k)`, not `h(x_{k+1})`). So in a loop, the returned `y` lags the returned state by one step.

2. **`rosnode.py`** — `ROSNode(*, dynamical_system, state_name=None, subs=None, pubs=None)`
   - `subs`: list of dicts: `topic`, `msg_type`, `arg` (kwarg name given to `step`), `ros2py`; optional `stale_after`/`buffer_size`/`use_msg_timestamp`.
   - `pubs`: list of dicts: `topic`, `msg_type`, `py2ros`; optional `key` (required with more than one publisher).
   - `state_name`: name of the `f`/`h` argument that is the block's state. The node keeps it internally, initializes it from `initial_state`, and updates it from the returned `x_next`. Read it via `.state`.
   - `step(**kwargs)` is pure Python/NumPy: it converts ROS messages in, runs the `DynamicalSystem`, converts results out. **No `rclpy` needed**; ROS messages are detected by duck-typing, so `rosnode.py` has no import-time ROS dependency.
   - `write_ROSNode_to_rclpy(path, *, node_name, sync_mode=None, timer_hz=None, stale_after=None, deps=None, initial_state=None, initial_inputs=None, static_params=None, dynamic_params=None, sub_noise=None, pub_noise=None)` only *emits* rclpy imports into the generated file. Deployment details (`node_name`, `sync_mode`, `timer_hz`) go here, not in the constructor.

3. **`ros2py_py2ros.py`** — converter functions
   - Individually named `ros2py_<type>` / `py2ros_<type>` pairs (e.g. `ros2py_float64`, `py2ros_float64`, `ros2py_imu`, `py2ros_imu`); **no registry dict**. Pass them explicitly in the `"ros2py"`/`"py2ros"` keys.
   - Covers geometry_msgs, nav_msgs, sensor_msgs, std_msgs, turtlesim. Imports `rclpy` and the ROS `*_msgs` packages at module level, so it needs a live ROS2 install.
   - To support a new message type, add a function pair here and document it in `docs/source/api/ros2py_py2ros.rst`.

4. **`__init__.py`** — eager: `DynamicalSystem`, `ROSNode`. Lazy via `__getattr__`: `ros2py_py2ros`.

### Generated-node semantics (important when explaining behavior)

- **`tk`**: the only reserved argument name, and optional. If an `f`/`h` declares `tk`, the generated node binds it to **wall-clock seconds since node start**. Nothing else is reserved.
- **Event-driven**: callbacks drive `step`. Only a source node with no inputs (e.g. a reference generator) needs `timer_hz`; the timer period is `1/timer_hz`. Every other node runs when its messages arrive.
- **`sync_mode="any"`**: step on every incoming message; an absent input is passed as `None`. **`"all"`**: step only when every subscription holds a fresh message, so a constant reference published once drives exactly one step; republish periodically.
- **Inputs are consumed**: once a buffered value has contributed to a step it is removed, so an unchanged input arrives as `None` on the next step rather than being reused. A new `/uk` never re-processes an old `/yk`.
- **`stale_after`** (seconds, per subscription): older messages are dropped to `None`.
- **`initial_inputs`**: a cold-start fallback used only until the first message *ever* arrives on that subscription (tracked by a `_<arg>_seen` flag). It is not a "last value" fallback. It breaks startup ordering deadlocks such as PID ↔ KF.
- **`static_params`** are baked in at generation; **`dynamic_params`** become ROS2 parameters tunable with `ros2 param set`.
- **Model time vs. node time**: simulation uses a `dt`; the node runs at the rate of its driver. Choose `timer_hz = 1/dt_ros`, pass `dt_ros` as a static param, and recompute any `dt`-dependent matrices (e.g. `Fk`, `Bk`, `Qk`) for `dt_ros`. Sim-time ≠ message-time otherwise.
- **`write_ROSNode_to_rclpy` requirements**: `f`/`h` must be **named functions** (no lambdas), their **source must be retrievable** (so not defined via `exec`, and notebooks are supported), **self-contained** (anything else they use goes in `deps=`), and every parameter without a default must be supplied via `static_params`/`dynamic_params`.

## Helping users (tutorial and package support)

The main tutorial is `docs/source/tutorials/0_cruise_control/cruise_control_with_dynamicalnodes.ipynb`, also the docs landing page's first link. It is self-contained, from installation to a live ROS graph, and mirrors the paper (section numbers in parentheses). Walk users through it in order:

| Section | What it covers |
|---|---|
| Overview + outline | Package shape and a linked outline |
| Installation (base) | `pip install dynamicalnodes`; collapsed; has a path check cell |
| Dynamical Systems (II-A), CTDS/DTDS | Theory: continuous- vs discrete-time systems, Euler discretization |
| The `DynamicalSystem` Class (III-B) | `.step()`, composing systems; car + speedometer, signal generators, harmonic oscillator examples |
| Discrete-time Diagrams (II-B) | Blocks and arrows ↔ systems and signals |
| Installation (ROS) | ROS2 + message packages; collapsed; check cell |
| The Robot Operating System (II-C), Workflow (III-A) | ROS vocabulary and the Theory→Python→ROS pipeline |
| The `ROSNode` Class (III-C) | Testing data translation, generating rclpy files, Sim Time to Node Time, running the nodes |
| Example: Car Cruise Control (IV) | Plant (A), reference (B), PID (C), Kalman filter (D), simulating the loop (E), generating/running the ROS graph, live PID tuning, running without the launch file |

How to help:
- **Installation**: the base package needs only `numpy`. The `ROSNode` section needs ROS2 (system packages: `rclpy`, `std_msgs`, etc., not on PyPI), and `ros2py_py2ros` always needs ROS2. `ROSNode.step()` itself does not, but the tutorial imports `Float64` and the converters, so the ROS part needs ROS2 installed and sourced.
- **Mental model**: every block is `(f, h)`. Write plain named functions with descriptive args (`xk`, `uk`, `dt`, …). `DynamicalSystem.step(**kwargs)` binds by name; no signature adapters are needed.
- **Debugging a loop**: remember `h` sees the pre-update state, and the state returned by `step` is the next one. Initialize every state and every feedback input before the first iteration (e.g. the PID's `xhatk` before the Kalman filter has run).
- **Debugging generated nodes**: check the `write_ROSNode_to_rclpy` requirements above first (lambdas, `exec`-defined functions, missing `deps`, missing params). Then `sync_mode`, `stale_after`, `timer_hz` and `initial_inputs`. For "node does nothing", the cause is usually `sync_mode="all"` plus an input that is not republished, or an input that is stale.
- **Estimator conventions**: the cruise-control Kalman filter is in matrix form (works for any state dimension; 1×1 here) and in **prior form**: state `ok = (x̂_{k|k-1}, P_{k|k-1})`; `fkf` *updates* with `yk` first, then *predicts* with `uk`; `hkf(ok)` returns the prior `x̂_{k|k-1}`. Use `float(xhat[0])` to feed a scalar PID. The estimate returned at step `k` reaches the controller at `k+1` (one-sample feedback delay). Under `sync_mode="any"` the node may see only one of `uk`/`yk`, so both are optional (`None` skips that half).
- **Variations**: other estimators/controllers only need new `f`/`h` functions; the pipeline is unchanged.
- Point users to the API pages for argument details rather than re-deriving them.
- **Skills** in `.claude/skills/` give step-by-step procedures; use them when a user's task matches: `discretize-f-h` (continuous-time → discrete-time `f`/`h`), `simulate-with-dynamicalsystem` (Python loops, feedback, estimators), `wrap-in-rosnode` (build `ROSNode`s and test the ROS-typed loop), `write-ros-converters` (new `ros2py_*`/`py2ros_*` pairs), `deploy-rosnodes-to-rclpy` (generate, run, debug nodes). The tutorial notebook and README point to them. Keep them consistent with this file and the tested notebook when the API changes. (`control-theory-specialist`, `documentation-generator` and `ros2-integration-expert` in the same folder are older, broader skills.)

## Development

### Testing
The project uses doctests. Run them on the source only; bare `pytest` at the repo root also tries to collect the tutorial `.py` node/launch files, which need ROS and fail collection.
```bash
pytest src                                                       # all doctests (8)
pytest --doctest-modules src/dynamicalnodes/dynamical_system.py  # one file
```
New functionality gets self-contained, ROS-free doctest examples (`NORMALIZE_WHITESPACE`/`ELLIPSIS` are set globally in `pyproject.toml`).

### Code quality
```bash
black src/ ; isort src/ ; mypy src/ ; flake8 src/
```

### Docs
```bash
cd docs && make html     # → docs/build/html/
make clean
```
Deploys to GitHub Pages via `.github/workflows/docs.yml` on push to `main`; PyPI publishing via `.github/workflows/publish.yml` on release. Build/publish: `python -m build`, `twine check dist/*`.

Docs conventions (`docs/source/conf.py`):
- Sphinx with `myst_nb`, autodoc, napoleon, `sphinx_rtd_theme`; `nb_execution_mode = "off"`, so **notebook outputs must be executed and saved in the notebook**. `rclpy` and ROS message packages are in `autodoc_mock_imports`.
- `myst_heading_anchors = 4` (slugs match the GitHub style used by notebook links like `#installation-base`). Each notebook has a single `#` title; headings `##`/`###`/`####` populate the sidebar. Outline links use anchors, with paper section numbers in parentheses.
- Docstrings that have a `Returns` section need a blank line before the next field list (otherwise: "Field list ends without a blank line").
- Landing page `docs/source/index.rst`: hidden toctrees "Tutorial" (the cruise-control notebook) and "Reference" (`api/index`). API pages: `api/dynamical_system.rst`, `api/rosnode.rst`, `api/ros2py_py2ros.rst`.

### Editing the tutorial notebook
- It is large (~1 MB with outputs); Read/Edit tools handle it poorly. Edit cells with a short `nbformat` script, then re-execute in place from the notebook's own directory (paths in cells are relative):
  ```bash
  cd docs/source/tutorials/0_cruise_control
  jupyter nbconvert --to notebook --execute --inplace cruise_control_with_dynamicalnodes.ipynb
  ```
  Running regenerates `plots/*.png`, `ros_nodes/*.py`, `toy_ros_nodes/*.py` and `ros_nodes/cruise_control.launch.py`. Check for `error` outputs afterward.
- Plotting cells and installation check cells carry the `hide-input` tag; keep new plot cells hidden. Plot cells save PNGs under `plots/`.
- Heading names are linked from the outline cell and elsewhere; renaming a heading means updating the links.
- Add a link to the API docs at the first mention of each API in a markdown cell (full `https://nehalsinghmangat.github.io/dynamicalnodes/api/...` URLs).
- Code listings in the paper are pasted from the notebook, so keep both in sync (the notebook is the tested source).

## Project Structure

```
src/dynamicalnodes/
├── __init__.py            # DynamicalSystem, ROSNode eager; ros2py_py2ros lazy
├── dynamical_system.py
├── rosnode.py
└── ros2py_py2ros.py

docs/
├── source/
│   ├── conf.py, index.rst, installation.rst, license.rst
│   ├── api/               # index, dynamical_system, rosnode, ros2py_py2ros (.rst)
│   ├── tutorials/
│   │   ├── 0_cruise_control/   # main tutorial notebook + generated nodes, plots, rqt/PlotJuggler assets
│   │   ├── harmonic_oscillator/  # oscillator notebooks (untracked)
│   │   ├── 1_gps_imu/, 2_multiple_systems/, modeling/, algorithms_as_dynamical_systems/  # older / WIP
│   ├── fh_library/        # WIP library of f/h pages (controllers, observers, plants)
│   └── _static/           # css, figures
└── Makefile, build/       # build/ is generated, not committed

paper/                     # IEEE conference paper (see below)
.claude/skills/            # Claude Code skills for users of the package (see Helping users); .claude/settings.local.json is local, don't commit
.github/workflows/         # docs.yml, publish.yml
```

Dependencies: core `numpy>=1.24`; dev `pytest`, `pytest-doctestplus`, `flake8`, `black`, `isort`, `mypy`, `build`, `twine`; docs `sphinx`, `sphinx-rtd-theme`, `sphinx-copybutton`, `myst_nb`, `sphinx-autodoc-typehints`, `matplotlib`, `scipy`, `jupyter`; ROS2 (system packages) `rclpy`, `geometry_msgs`, `sensor_msgs`, `nav_msgs`, `std_msgs`, `turtlesim`.

### Working-tree cautions
- The tree has a lot of uncommitted work and older stashes. **Do not use `git stash`** (it removes uncommitted edits to tracked files); do not discard changes without asking.
- Known leftovers, not yet cleaned up: untracked `docs/source/tutorials/0_cruise_control/0_cruise_control.ipynb` (an older notebook version that differs from the committed one; check before deleting); an emacs lock file `.#cruise_control_with_dynamicalnodes.ipynb` (transient); `harmonic_oscillator_in_ros.ipynb` still uses the old `.eval(` API; Sphinx warns about pages not in any toctree (`installation.rst`, `license.rst`, `tutorials/index.rst`, `fh_library/index.ipynb`). `pid_tuning_layout.xml` and `rosgraph.svg` in the cruise-control folder are kept on purpose though the notebook doesn't reference them. `plots/dt_oscillator_step.png` is referenced by a markdown image but no cell regenerates it. The root `main.tex` is an older file, not the paper.

## Paper (`paper/`)

IEEE conference paper (theory → Python → ROS pipeline with a cruise-control example). Single-file LaTeX: all text in `paper/main.tex`; no subfiles.

### Build
```bash
cd paper
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```
Build artifacts (`.aux`, `.log`, `.bbl`, …) should not be kept in `paper/`. When checking a build, prefer an out-of-tree directory: `pdflatex -output-directory=<scratch> main.tex` (copy `references.bib` there for `bibtex`). The first pass shows `??` for forward `\ref`s until a second run. Currently 11 pages.

### Files
| File | Role |
|------|------|
| `paper/main.tex` | The whole paper |
| `paper/references.bib` | Bibliography (`\bibliography{references}`, `unsrtnat`, cite with `\citep{}`) |
| `paper/figures/` | Figures, referenced by file name (`\graphicspath{{figures/}}`) |

Figures: `feedback_system.pdf`, `ros_graph.pdf` (three nodes: publisher + two subscribers; included at `0.7\columnwidth` so the page count stays 11; the older two-node `ros_graph_2.pdf` is unused), `overview_theory.pdf`, `overview_python.pdf`, `overview_ros.pdf`, `modularity.pdf`, `syncmode_any.pdf`, `syncmode_all.pdf`, `first_step.pdf`, `rqt_graph.pdf`, `python_output.png`, `ros_output.png` (PlotJuggler capture of the live nodes). Figure sources are not in the repo; older copies live under `~/academic/writing/dynamicalnodes*/`.

### Formatting (IEEEtran)
- `\documentclass[conference]{IEEEtran}`, two columns; `amsmath`, `amssymb`, `graphicx`, `subcaption`, `caption`, `float`, `stfloats`, `listings` (Python; `\lstset` in the preamble).
- Sections I–VIII: Intro, Background, Framework (A–E), Example: Car Cruise Control (IV-A … IV-F), Relation to Other Software, Conclusion, Acknowledgements, Author Contributions.
- Listings are **not floats**: plain `lstlisting` + `\captionof{figure}{…}` then `\label{…}` (label after the caption, or `\ref` gives the section number). They can split across columns/pages. Keep lines short enough not to wrap (shorten comments; `\scriptsize` where needed).
- `\newpage` ends a column; `\clearpage` ends a page and flushes floats. `figure*` can only float to the top or bottom of a page.
- Layout is hand-tuned (code and figures sit under the text introducing them). After any edit, recompile and check the rendered pages.
- Section IV: IV-E "Simulating the Cruise Control System" has the Python loop listing, then the Python plot in the same column; IV-F "Writing to ROS" has the ROS listing followed by the `rqt_graph` and ROS plot images in the right column.

### Status of reviewer items
Done: model time vs. message time (III-C, ties to "Sim Time to Node Time" in the notebook); III-C Figs. 4–5 listings from the notebook; Section IV listings from the notebook (matrix-form Kalman filter); III-E semantics (`sync_mode="any"` consumes inputs; `"all"` needs a fresh message on every subscription); Kalman time indices (prior form, update-then-predict, one-cycle description in IV-D).

Open:
- `\ref{subsubsec:car_with_control}` is undefined (shows `??` in IV-B).
- Paper III-D listings (translation functions, state-augmented `hcar`) still use the older API.
- Speedometer uses `|v_k|` but the Kalman filter assumes a linear measurement model (valid only for v ≥ 0).
- `python_output.png` and `ros_output.png` come from different (and older) runs; a like-for-like comparison (same reference, gains, noise seed, Δt, plus a delayed-message case) is still needed.
- Under `sync_mode="any"` in the live graph the Kalman node usually sees `/uk` before `/yk`, so it predicts before it updates with a measurement of the earlier state. Either use `sync_mode="all"` for that node or state it as an approximation.
