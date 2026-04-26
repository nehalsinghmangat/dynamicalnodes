# Bibliography System - Implementation Tracking with Colored Circles

## Overview

The new bibliography system tracks paper implementations across three platforms:
- 🔵 **dynamicalnodes core** (blue circle) - Generic algorithm implementation
- 🟢 **TurtleBot** (green circle) - TurtleBot-specific implementation
- 🟡 **Crazyflie** (yellow circle) - Crazyflie-specific implementation
- ⚫ **Not implemented** (gray circle) - No implementation yet

Each colored circle is **clickable** and links directly to a self-contained, downloadable Jupyter notebook demonstrating the implementation.

## Quick Start

### 1. Add a Paper with Implementation

```bibtex
@article{smith2024mpc,
  title        = {Model Predictive Control for Quadrotors},
  author       = {Smith, John},
  journal      = {Robotics Journal},
  year         = {2024},
  url          = {https://arxiv.org/abs/2401.12345},
  keywords     = {control, trajectory-planning},
  dynamicalnodes_category = {mpc},
  impl_dynamicalnodes   = {examples/mpc_demo.ipynb},
  impl_turtlebot = {},
  impl_crazyflie = {examples/mpc_crazyflie.ipynb},
  note         = {MPC implementation for quadrotors}
}
```

### 2. Create the Jupyter Notebook

Create a self-contained notebook at the path you specified (e.g., `docs/source/examples/mpc_crazyflie.ipynb`):

```python
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# MPC for Crazyflie\n",
    "**Paper:** Smith (2024) - Model Predictive Control for Quadrotors\n",
    "..."
   ]
  }
 ]
}
```

### 3. Generate Metadata and Build

```bash
python3 docs/generate_bib_metadata.py
cd docs && make html
```

### 4. Result

Users will see your paper with colored circles. Clicking the yellow Crazyflie circle opens the notebook!

## BibTeX Fields Reference

### Required Fields

Standard BibTeX fields:
- `title`, `author`, `year`, `journal`/`booktitle`
- `url` - Link to arXiv or DOI

### Custom dynamicalnodes Fields

**`keywords`** - Broad categories (comma-separated)
- Options: `state-estimation`, `control`, `planning`, `filtering`, etc.
```bibtex
keywords = {control, trajectory-planning}
```

**`dynamicalnodes_category`** - Specific algorithm
- Options: `kalman-filter`, `ekf`, `ukf`, `pid`, `mpc`, `lqr`, etc.
```bibtex
dynamicalnodes_category = {mpc}
```

**`impl_dynamicalnodes`** - Path to dynamicalnodes core implementation notebook
- Empty `{}` if not implemented
- Relative path from `docs/source/`
```bibtex
impl_dynamicalnodes = {examples/kalman_filter_demo.ipynb}
```

**`impl_turtlebot`** - Path to TurtleBot implementation notebook
```bibtex
impl_turtlebot = {examples/kf_turtlebot.ipynb}
```

**`impl_crazyflie`** - Path to Crazyflie implementation notebook
```bibtex
impl_crazyflie = {examples/mpc_crazyflie.ipynb}
```

**`note`** - Brief description and context
```bibtex
note = {Classic Kalman filter. Implementations for dynamicalnodes core and TurtleBot}
```

## Filter Behavior

### Category Filter
Shows papers matching selected category from `keywords` field.

### Algorithm Filter
Shows papers matching selected algorithm from `dynamicalnodes_category` field.

### Implementation Status (Radio Buttons)
- **Show All** - All papers regardless of implementation
- **Not Yet Implemented** - Papers with no implementations (all impl fields empty)
- **Implemented in dynamicalnodes** - Papers with `impl_dynamicalnodes` set
- **Implemented for TurtleBot** - Papers with `impl_turtlebot` set
- **Implemented for Crazyflie** - Papers with `impl_crazyflie` set

## Creating Implementation Notebooks

### Requirements for Notebooks

1. **Self-Contained** - Include all necessary imports and setup
2. **Downloadable** - Mention download instructions in the notebook
3. **Runnable** - Users should be able to run it locally
4. **Well-Documented** - Explain the algorithm and implementation

### Notebook Template

```jupyter
{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# [Algorithm Name] for [Platform]\n",
    "\n",
    "**Paper:** Author (Year) - Paper Title\n",
    "\n",
    "**Implementation:** [Brief description]\n",
    "\n",
    "## Download\n",
    "\n",
    "Download this notebook:\n",
    "- Click File → Download as → Notebook (.ipynb)\n",
    "\n",
    "## Requirements\n",
    "\n",
    "```bash\n",
    "pip install numpy matplotlib dynamicalnodes\n",
    "```"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "import numpy as np\n",
    "import matplotlib.pyplot as plt\n",
    "from dynamicalnodes import DynamicalSystem\n",
    "# ... your imports"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Algorithm Explanation\n",
    "[Explain the algorithm]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Implementation code\n",
    "..."
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Results\n",
    "[Show results with plots]"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Conclusion\n",
    "\n",
    "## Next Steps\n",
    "\n",
    "## References\n",
    "- Author (Year). Paper title\n",
    "- dynamicalnodes docs: https://dynamicalnodes.readthedocs.io"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
```

## Complete Workflow Example

Let's implement an Extended Kalman Filter for TurtleBot:

### Step 1: Add to references.bib

```bibtex
@article{smith2020ekf,
  title        = {Extended Kalman Filtering for Mobile Robots},
  author       = {Smith, Jane},
  journal      = {IEEE Robotics},
  year         = {2020},
  url          = {https://arxiv.org/abs/2001.12345},
  keywords     = {state-estimation, filtering, nonlinear},
  dynamicalnodes_category = {ekf},
  impl_dynamicalnodes   = {examples/ekf_demo.ipynb},
  impl_turtlebot = {examples/ekf_turtlebot.ipynb},
  impl_crazyflie = {},
  note         = {EKF for nonlinear state estimation. Implemented for dynamicalnodes and TurtleBot}
}
```

### Step 2: Create Notebooks

Create two notebooks:
- `docs/source/examples/ekf_demo.ipynb` - Generic EKF
- `docs/source/examples/ekf_turtlebot.ipynb` - TurtleBot-specific

### Step 3: Generate & Build

```bash
# Generate metadata from BibTeX
python3 docs/generate_bib_metadata.py

# Build docs
cd docs
make html

# Open in browser
firefox build/html/bibliography.html
```

### Step 4: Test

1. Go to bibliography page
2. See the paper with 🔵 blue and 🟢 green circles
3. Click blue circle → opens `ekf_demo.html`
4. Click green circle → opens `ekf_turtlebot.html`
5. Users can download the `.ipynb` files from the notebook pages

## File Organization

```
docs/
├── source/
│   ├── references.bib                    # Your bibliography
│   ├── bibliography.rst                  # Filter UI
│   ├── examples/                         # Implementation notebooks
│   │   ├── kf_turtlebot_demo.ipynb      # Example notebook
│   │   ├── ekf_demo.ipynb               # Your dynamicalnodes core impl
│   │   └── ekf_turtlebot.ipynb          # Your TurtleBot impl
│   └── _static/
│       ├── css/
│       │   └── bibliography.css          # Colored circles styling
│       └── js/
│           ├── bib_metadata.js           # AUTO-GENERATED
│           └── bibliography.js           # Filter logic
└── generate_bib_metadata.py              # Run after editing .bib
```

## Colors and Visual Design

### Circle Colors
- 🔵 Blue (`#007bff`) - dynamicalnodes core
- 🟢 Green (`#28a745`) - TurtleBot
- 🟡 Yellow (`#ffc107`) - Crazyflie
- ⚫ Gray (`#6c757d`) - Not implemented

### Border Colors
Citations get a left border matching their primary implementation:
- Blue border → Has dynamicalnodes core implementation
- Green border → Has TurtleBot implementation
- Yellow border → Has Crazyflie implementation

### Hover Effects
- Circles scale up 20% on hover
- Cursor becomes pointer for clickable circles
- Gray circles (not implemented) are slightly transparent

## User Experience

### Filtering Workflow
1. User selects "Control" category
2. User selects "MPC" algorithm
3. User clicks "Implemented for Crazyflie" radio button
4. **Result:** Only MPC papers implemented for Crazyflie show up
5. User clicks yellow circle → Opens Crazyflie MPC notebook
6. User downloads `.ipynb` and runs locally

### Download Workflow
1. User finds interesting paper with implementation
2. Clicks colored circle
3. Jupyter notebook opens in docs
4. User scrolls through to understand implementation
5. User downloads notebook using browser or instructions
6. User runs notebook locally with their own data

## Troubleshooting

**Circles not appearing:**
- Check that impl fields are not empty: `impl_dynamicalnodes = {path}` not `impl_dynamicalnodes = {}`
- Regenerate metadata: `python3 generate_bib_metadata.py`
- Rebuild docs: `make html`

**Circles not clickable:**
- Verify notebook path exists: `docs/source/examples/your_notebook.ipynb`
- Path should be relative to `docs/source/`
- Notebook must have `.ipynb` extension

**Wrong paper gets circles:**
- Check BibTeX key format: `authorYEARkeyword`
- Ensure year in key matches year in entry
- Make keys unique and descriptive

**Filter not working:**
- Open browser console (F12) for JavaScript errors
- Check that metadata was regenerated
- Verify filter values match your custom fields

## Best Practices

✅ **DO:**
- Create one notebook per implementation (dynamicalnodes, TurtleBot, Crazyflie)
- Make notebooks fully self-contained and runnable
- Include download instructions in notebooks
- Use relative paths from `docs/source/`
- Run `generate_bib_metadata.py` after editing `.bib`
- Test notebooks locally before committing

❌ **DON'T:**
- Put absolute paths in impl fields
- Forget to regenerate metadata after .bib changes
- Create notebooks that depend on external files
- Use `.py` files instead of `.ipynb` notebooks
- Edit `bib_metadata.js` manually (it's auto-generated)

## Maintenance

**When you add a new paper:**
1. Edit `references.bib`
2. Create notebook(s) if implemented
3. Run `generate_bib_metadata.py`
4. Run `make html`
5. Test in browser

**When you implement an algorithm:**
1. Update the paper's impl field in `references.bib`
2. Create the implementation notebook
3. Regenerate and rebuild
4. Commit both `.bib` and `.ipynb` files

**When you add a new robot platform:**
1. Add new field: `impl_newrobot = {...}` in `.bib`
2. Update `generate_bib_metadata.py` to extract it
3. Add radio button in `bibliography.rst`
4. Add circle color in `bibliography.css`
5. Update filter logic in `bibliography.js`
