# Bibliography Quick Reference

## Adding a Paper (Copy & Paste Template)

```bibtex
@article{authorYEARkeyword,
  title={Paper Title Here},
  author={Last, First and Another, Name},
  journal={Journal or Conference Name},
  volume={X},
  number={Y},
  pages={1--10},
  year={YEAR},
  url={https://arxiv.org/abs/XXXX.XXXXX},
  keywords={PICK: state-estimation OR control OR planning},
  dynamicalnodes_category={PICK: kalman-filter, ekf, ukf, pid, mpc, lqr, etc.},
  dynamicalnodes_observability={PICK: full OR partial},
  dynamicalnodes_robot={PICK: turtlebot, crazyflie, generic, etc.},
  dynamicalnodes_implemented={PICK: yes, planned, no},
  note={Brief description. If implemented: "Implementation in dynamicalnodes.module.path"}
}
```

## Citing a Paper

**In .rst files:**
```rst
:cite:`authorYEARkeyword`
```

**In .md files (with MyST):**
```markdown
{cite}`authorYEARkeyword`
```

## Common Categories

### Keywords (Broad)
- `state-estimation`
- `control`
- `planning`
- `filtering`
- `localization`
- `trajectory-planning`

### Algorithm Categories
- `kalman-filter` - Classic KF
- `ekf` - Extended Kalman Filter
- `ukf` - Unscented Kalman Filter
- `particle-filter` - Particle Filter
- `pid` - PID Controller
- `mpc` - Model Predictive Control
- `lqr` - Linear Quadratic Regulator
- `slam` - SLAM algorithms

### Robots
- `generic` - Works on any platform
- `turtlebot` - TurtleBot specific
- `crazyflie` - Crazyflie specific
- `quadrotor` - Generic quadrotor
- `ground-robot` - Generic ground robot

## Build Commands

```bash
# Install dependencies
pip install -e ".[docs]"

# Build docs
cd docs
make html

# Clean build
make clean && make html

# View locally
open build/html/bibliography.html
```

## File Locations

- Add papers: `docs/source/references.bib`
- View bibliography page: `docs/source/bibliography.rst`
- Custom styles: `docs/source/_static/css/bibliography.css`
- Filter logic: `docs/source/_static/js/bibliography.js`

## Implementation Workflow

1. Find paper → Add to `references.bib` with `dynamicalnodes_implemented=no`
2. Plan implementation → Update to `dynamicalnodes_implemented=planned`
3. Implement → Update to `dynamicalnodes_implemented=yes`, add module path to note
4. Cite in docs → Use `:cite:`key`` in relevant pages
5. Push → ReadTheDocs rebuilds automatically

## Quick Examples

### Implemented Algorithm
```bibtex
@article{kalman1960,
  title={A new approach to linear filtering},
  author={Kalman, R. E.},
  year={1960},
  url={https://doi.org/10.1115/1.3662552},
  keywords={state-estimation, filtering},
  dynamicalnodes_category={kalman-filter},
  dynamicalnodes_observability={full},
  dynamicalnodes_robot={generic},
  dynamicalnodes_implemented={yes},
  note={Classic KF. Implementation: dynamicalnodes.utilities.estimators.kf}
}
```

### Planned Algorithm
```bibtex
@inproceedings{julier1997ukf,
  title={Unscented Kalman Filter},
  author={Julier, S. J. and Uhlmann, J. K.},
  year={1997},
  url={https://doi.org/10.1117/12.280797},
  keywords={state-estimation, filtering, nonlinear},
  dynamicalnodes_category={ukf},
  dynamicalnodes_observability={full},
  dynamicalnodes_robot={generic},
  dynamicalnodes_implemented={planned},
  note={UKF for nonlinear systems. Planned for v0.3}
}
```

### Robot-Specific Paper
```bibtex
@article{mellinger2011mpc,
  title={MPC for Quadrotors},
  author={Mellinger, D.},
  year={2011},
  url={https://example.com/paper},
  keywords={control, trajectory-planning},
  dynamicalnodes_category={mpc},
  dynamicalnodes_observability={full},
  dynamicalnodes_robot={crazyflie},
  dynamicalnodes_implemented={planned},
  note={MPC controller optimized for Crazyflie platform}
}
```
