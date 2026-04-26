# Adding References to the dynamicalnodes Bibliography

This guide explains how to add new papers to the dynamicalnodes bibliography so they work correctly with the filterable visualization system.

## Quick Checklist

When adding a new paper:
- [ ] Use correct BibTeX key format: `authorYEARkeyword` (e.g., `kalman1960new`)
- [ ] Include all required standard fields
- [ ] Add custom dynamicalnodes fields: `keywords`, `dynamicalnodes_category`, `impl_*`, `note`
- [ ] Set implementation paths or empty `{}` for each platform
- [ ] Run `python3 docs/generate_bib_metadata.py`
- [ ] Build docs: `cd docs && make html`
- [ ] Test filtering in browser

## BibTeX Key Format (CRITICAL)

The visualization system matches citations to metadata using the BibTeX key. **You must follow this format exactly:**

```
authorYEARkeyword
```

### Format Rules

1. **Author part**: First author's last name, lowercase, letters only
2. **Year part**: 4-digit publication year
3. **Keyword part**: Short descriptor (optional but recommended)
4. **No spaces, no underscores, no special characters**

### Examples

✅ **GOOD:**
- `kalman1960new` - Matches "Kalman" in "Rudolph Emil Kalman. ... 1960"
- `julier1997new` - Matches "Julier" in "Simon J Julier ... 1997"
- `thrun2005probabilistic` - Matches "Thrun" in "Sebastian Thrun ... 2005"
- `smith2024mpc` - Matches "Smith" in "John Smith ... 2024"

❌ **BAD:**
- `Kalman1960` - Capital letter won't match (case-sensitive in regex)
- `kalman_1960_new` - Underscores break the matching
- `kalman-filter-1960` - Dashes break the matching
- `1960kalman` - Year must come after author name
- `kalmanrudolph1960` - Too much of the author name (won't match "Kalman")

### Why This Matters

The JavaScript extracts the author name using:
```javascript
const authorMatch = key.match(/^([a-z]+)/i);  // Everything before first digit
```

For `kalman1960new`:
- Extracts: `"kalman"`
- Searches citation text for: `"kalman"` (case-insensitive)
- Finds: `"Kalman"` in "Rudolph Emil Kalman"
- ✓ Match successful

For `kalmanrudolph1960new`:
- Extracts: `"kalmanrudolph"`
- Searches citation text for: `"kalmanrudolph"`
- Doesn't find it in "Rudolph Emil Kalman"
- ✗ Match fails - no circles appear

## Required Standard BibTeX Fields

Include these standard fields for all entries:

```bibtex
@article{authorYEARkeyword,
  title        = {Paper Title},
  author       = {Last Name, First Name and Other, Author},
  journal      = {Journal Name},  % or booktitle for @inproceedings
  year         = {2024},
  url          = {https://doi.org/... or https://arxiv.org/abs/...},
}
```

### Field Guidelines

- **title**: Full paper title (no LaTeX formatting like `\texttt{}`)
- **author**: Full author list with "and" separator
- **journal** or **booktitle**: Publication venue
- **year**: 4-digit year (must match year in BibTeX key)
- **url**: Link to paper (DOI preferred, arXiv acceptable)

## Required Custom dynamicalnodes Fields

Add these custom fields to every entry:

```bibtex
@article{kalman1960new,
  % ... standard fields ...
  keywords       = {state-estimation, filtering},
  dynamicalnodes_category = {kalman-filter},
  impl_dynamicalnodes     = {examples/kf_demo.ipynb},
  impl_turtlebot = {examples/kf_turtlebot.ipynb},
  impl_crazyflie = {},
  note           = {Classic Kalman filter. Implementations for dynamicalnodes and TurtleBot}
}
```

### Custom Field Descriptions

**`keywords`** - Broad categories (comma-separated, no spaces after commas)
- Used by: Category filter dropdown
- Format: `keyword1,keyword2,keyword3`
- Options:
  - `state-estimation` - Estimation and filtering algorithms
  - `control` - Control algorithms (PID, MPC, LQR, etc.)
  - `planning` - Path planning and trajectory optimization
  - `filtering` - General filtering techniques
  - `nonlinear` - Nonlinear methods
  - `optimization` - Optimization-based approaches
  - `robotics` - General robotics
  - `localization` - Localization and SLAM
  - Add others as needed

**`dynamicalnodes_category`** - Specific algorithm type (single value)
- Used by: Algorithm filter dropdown
- Format: `algorithm-name` (lowercase, hyphenated)
- Options:
  - `kalman-filter` - Standard Kalman Filter
  - `ekf` - Extended Kalman Filter
  - `ukf` - Unscented Kalman Filter
  - `pid` - PID controller
  - `mpc` - Model Predictive Control
  - `lqr` - Linear Quadratic Regulator
  - `particle-filter` - Particle Filter
  - `slam` - SLAM algorithms
  - Add to `docs/source/bibliography.rst` dropdown when adding new types

**`impl_dynamicalnodes`** - Path to dynamicalnodes core implementation notebook
- Used by: Blue circle (🔵)
- Format: `path/to/notebook.ipynb` (relative to `docs/source/`)
- Set to `{}` if not implemented
- Example: `examples/kalman_filter_demo.ipynb`

**`impl_turtlebot`** - Path to TurtleBot implementation notebook
- Used by: Green circle (🟢)
- Format: `path/to/notebook.ipynb` (relative to `docs/source/`)
- Set to `{}` if not implemented
- Example: `examples/kf_turtlebot.ipynb`

**`impl_crazyflie`** - Path to Crazyflie implementation notebook
- Used by: Yellow circle (🟡)
- Format: `path/to/notebook.ipynb` (relative to `docs/source/`)
- Set to `{}` if not implemented
- Example: `examples/mpc_crazyflie.ipynb`

**`note`** - Brief description (1-2 sentences)
- Used by: Appears in rendered bibliography
- Format: Plain text, no LaTeX commands
- Include: Brief context and which platforms are implemented
- Example: `Classic Kalman filter paper. Implementations available in dynamicalnodes core and TurtleBot`

## Complete Example

Here's a complete, correctly formatted entry:

```bibtex
@article{kalman1960new,
  title          = {A new approach to linear filtering and prediction problems},
  author         = {Kalman, Rudolph Emil},
  journal        = {Journal of Basic Engineering},
  volume         = {82},
  number         = {1},
  pages          = {35--45},
  year           = {1960},
  publisher      = {American Society of Mechanical Engineers},
  url            = {https://doi.org/10.1115/1.3662552},
  keywords       = {state-estimation,filtering},
  dynamicalnodes_category = {kalman-filter},
  impl_dynamicalnodes     = {theory_to_software/estimators/kalman_filters/standard_kalman_filter.ipynb},
  impl_turtlebot = {examples/kf_turtlebot_demo.ipynb},
  impl_crazyflie = {},
  note           = {Classic Kalman filter paper. Implementations available in dynamicalnodes core and TurtleBot}
}
```

This will produce:
- 🔵 Blue circle → links to `theory_to_software/estimators/kalman_filters/standard_kalman_filter.html`
- 🟢 Green circle → links to `examples/kf_turtlebot_demo.html`
- Appears when filtering for "state-estimation" or "filtering" categories
- Appears when filtering for "kalman-filter" algorithm
- Appears when filtering for "dynamicalnodes" or "turtlebot" implementations

## Common Entry Types

### Paper Not Yet Implemented

```bibtex
@inproceedings{julier1997new,
  title          = {New extension of the Kalman filter to nonlinear systems},
  author         = {Julier, Simon J and Uhlmann, Jeffrey K},
  booktitle      = {Signal processing, sensor fusion, and target recognition VI},
  volume         = {3068},
  pages          = {182--193},
  year           = {1997},
  organization   = {SPIE},
  url            = {https://doi.org/10.1117/12.280797},
  keywords       = {state-estimation,filtering,nonlinear},
  dynamicalnodes_category = {ukf},
  impl_dynamicalnodes     = {},
  impl_turtlebot = {},
  impl_crazyflie = {},
  note           = {Unscented Kalman Filter (UKF). Not yet implemented}
}
```

Result: ⚫ Single gray circle (not implemented)

### Paper Implemented Only in dynamicalnodes Core

```bibtex
@article{zarchan2013fundamentals,
  title          = {Fundamentals of Kalman filtering: a practical approach},
  author         = {Zarchan, Paul and Musoff, Howard},
  journal        = {American Institute of Aeronautics and Astronautics},
  year           = {2013},
  url            = {https://doi.org/10.2514/4.867200},
  keywords       = {state-estimation,filtering},
  dynamicalnodes_category = {kalman-filter},
  impl_dynamicalnodes     = {examples/kf_fundamentals.ipynb},
  impl_turtlebot = {},
  impl_crazyflie = {},
  note           = {Kalman filter fundamentals with practical examples. Generic implementation in dynamicalnodes core}
}
```

Result: 🔵 Blue circle only

### Paper Implemented on All Platforms

```bibtex
@article{smith2024mpc,
  title          = {Model Predictive Control for Quadrotors},
  author         = {Smith, Jane},
  journal        = {IEEE Robotics},
  year           = {2024},
  url            = {https://arxiv.org/abs/2401.12345},
  keywords       = {control,planning,optimization},
  dynamicalnodes_category = {mpc},
  impl_dynamicalnodes     = {examples/mpc_demo.ipynb},
  impl_turtlebot = {examples/mpc_turtlebot.ipynb},
  impl_crazyflie = {examples/mpc_crazyflie.ipynb},
  note           = {MPC for quadrotor control. Fully implemented across all platforms}
}
```

Result: 🔵🟢🟡 Blue, green, and yellow circles

## Workflow for Adding a New Paper

### 1. Add to references.bib

Edit `docs/source/references.bib` and add your entry following the format above:

```bash
# Open the bibliography file
vim docs/source/references.bib  # or your preferred editor
```

### 2. Create Implementation Notebooks (if applicable)

If the algorithm is implemented, create self-contained Jupyter notebooks:

```bash
# Example: creating a TurtleBot implementation
touch docs/source/examples/my_algorithm_turtlebot.ipynb
```

**Notebook requirements:**
- Self-contained (all imports, setup, and dependencies)
- Includes download instructions
- Links back to the paper
- Shows clear implementation and results
- Can be run standalone by users

See `docs/source/examples/kf_turtlebot_demo.ipynb` for a complete example.

### 3. Generate Metadata

Run the metadata generator to extract custom fields:

```bash
cd docs
python3 generate_bib_metadata.py
```

This creates/updates `docs/source/_static/js/bib_metadata.js`.

### 4. Build Documentation

```bash
cd docs
make html
```

### 5. Test in Browser

Open `docs/build/html/bibliography.html` in a browser:

```bash
firefox build/html/bibliography.html
# or
google-chrome build/html/bibliography.html
# or
open build/html/bibliography.html  # macOS
```

**Test checklist:**
- [ ] Paper appears in bibliography
- [ ] Correct colored circles appear
- [ ] Circles are clickable
- [ ] Category filter works
- [ ] Algorithm filter works
- [ ] Implementation status filter works
- [ ] Clicking circles navigates to notebooks
- [ ] Notebooks display correctly

### 6. Commit Changes

```bash
git add docs/source/references.bib
git add docs/source/_static/js/bib_metadata.js
git add docs/source/examples/*.ipynb  # if you added notebooks
git commit -m "Add reference: AuthorYEAR - Paper Title"
git push
```

## Troubleshooting

### Circles Don't Appear

**Symptom:** Paper shows in bibliography but no colored circles

**Possible causes:**
1. **BibTeX key format wrong** - Must be `authorYEARkeyword`
   - Fix: Rename key to `firstauthorlastname` + `year` + `descriptor`
   - Example: Change `kalman_1960` to `kalman1960new`

2. **Author extraction fails** - First part of key doesn't match citation text
   - Fix: Ensure key starts with first author's last name exactly
   - Example: For "Julier, Simon J" → use `julier1997...` not `simon1997...`

3. **Year mismatch** - Year in key doesn't match year in entry
   - Fix: Ensure `year = {1960}` matches `1960` in `kalman1960new`

4. **Metadata not regenerated** - Old metadata cached
   - Fix: Run `python3 docs/generate_bib_metadata.py` again

5. **Browser cache** - Old JavaScript cached
   - Fix: Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)

### Circles Don't Link Correctly

**Symptom:** Circles appear but clicking does nothing or gives 404

**Possible causes:**
1. **Wrong path in impl field** - Path doesn't exist
   - Fix: Verify notebook exists at `docs/source/path/to/notebook.ipynb`

2. **Path not relative to docs/source/** - Absolute path used
   - Fix: Use `examples/notebook.ipynb`, not `/home/user/docs/source/examples/notebook.ipynb`

3. **Notebook not built** - Sphinx didn't convert `.ipynb` to `.html`
   - Fix: Ensure `nbsphinx` is installed and configured in `conf.py`

### Filtering Doesn't Work

**Symptom:** Selecting filters doesn't change what papers are shown

**Possible causes:**
1. **Metadata not generated** - JavaScript object empty
   - Fix: Run `python3 docs/generate_bib_metadata.py`

2. **Custom fields missing** - No `keywords` or `dynamicalnodes_category`
   - Fix: Add all required custom fields to BibTeX entry

3. **Browser console errors** - JavaScript failing
   - Fix: Open browser console (F12) and check for errors

## Adding New Algorithm Types

If you're adding a paper with a new algorithm type not in the dropdown:

1. **Add to BibTeX** with new `dynamicalnodes_category`:
   ```bibtex
   dynamicalnodes_category = {new-algorithm-name}
   ```

2. **Update bibliography.rst** to add dropdown option:
   ```rst
   <select id="algorithm-filter" class="filter-select">
     <option value="all">All</option>
     <!-- existing options -->
     <option value="new-algorithm-name">New Algorithm Display Name</option>
   </select>
   ```

3. **Regenerate and rebuild**:
   ```bash
   python3 docs/generate_bib_metadata.py
   cd docs && make html
   ```

## Adding New Robot Platforms

To add a fourth platform (e.g., "Husky"), you need to:

1. **Add BibTeX field** to entries:
   ```bibtex
   impl_husky = {examples/algorithm_husky.ipynb}
   ```

2. **Update generate_bib_metadata.py** to extract it:
   ```python
   'impl_husky': get_field('impl_husky'),
   ```

3. **Add radio button** in `bibliography.rst`:
   ```rst
   <label class="radio-label">
     <input type="radio" name="impl-filter" value="husky">
     <span class="impl-circle impl-husky"></span>
     <span class="radio-text">Implemented for Husky</span>
   </label>
   ```

4. **Add CSS color** in `_static/css/bibliography.css`:
   ```css
   .impl-husky {
     background-color: #ff6b6b; /* Red */
   }
   ```

5. **Update JavaScript** in `_static/js/bibliography.js`:
   ```javascript
   const implementations = [
     { key: 'impl_dynamicalnodes', class: 'impl-dynamicalnodes', label: 'dynamicalnodes core', url: metadata.impl_dynamicalnodes },
     { key: 'impl_turtlebot', class: 'impl-turtlebot', label: 'TurtleBot', url: metadata.impl_turtlebot },
     { key: 'impl_crazyflie', class: 'impl-crazyflie', label: 'Crazyflie', url: metadata.impl_crazyflie },
     { key: 'impl_husky', class: 'impl-husky', label: 'Husky', url: metadata.impl_husky }
   ];
   ```

6. **Add filter logic** in `bibliography.js`:
   ```javascript
   } else if (implValue === 'husky') {
       if (!implHusky) {
           visible = false;
       }
   }
   ```

## Best Practices

✅ **DO:**
- Use consistent BibTeX key format: `authorYEARkeyword`
- Keep first author's last name as-is from the paper
- Use 4-digit years
- Set empty `{}` for unimplemented platforms (not omit the field)
- Add descriptive notes mentioning implementation status
- Test in browser before committing
- Create self-contained, downloadable notebooks
- Regenerate metadata after editing `.bib` file

❌ **DON'T:**
- Use underscores or hyphens in BibTeX keys
- Start keys with the year
- Use capital letters at the start of keys
- Omit impl_* fields (use `{}` instead)
- Use LaTeX commands in note field
- Forget to run `generate_bib_metadata.py`
- Use absolute paths for notebook locations
- Create notebooks that depend on external files

## File Locations Summary

```
docs/
├── source/
│   ├── references.bib                      # ← Edit this to add papers
│   ├── bibliography.rst                    # ← Filter UI (edit for new algorithms)
│   ├── examples/                           # ← Put implementation notebooks here
│   │   ├── kf_turtlebot_demo.ipynb
│   │   └── your_new_notebook.ipynb
│   └── _static/
│       ├── css/
│       │   └── bibliography.css            # ← Circle colors (edit for new platforms)
│       └── js/
│           ├── bib_metadata.js             # ← AUTO-GENERATED (don't edit)
│           └── bibliography.js             # ← Filter logic (edit for new platforms)
└── generate_bib_metadata.py                # ← Run this after editing .bib
```

## Quick Reference Card

```bibtex
@article{AUTHOR+YEAR+keyword,              % lowercase, no spaces/underscores
  title          = {Title},                 % no LaTeX formatting
  author         = {Last, First and ...},   % standard format
  journal        = {Journal Name},          % or booktitle
  year           = {YEAR},                  % matches key
  url            = {https://doi.org/...},   % DOI or arXiv
  keywords       = {cat1,cat2,cat3},        % comma-separated, no spaces
  dynamicalnodes_category = {algorithm-type},        % single value, hyphenated
  impl_dynamicalnodes     = {path/to/nb.ipynb},      % or {} if not implemented
  impl_turtlebot = {path/to/nb.ipynb},      % or {}
  impl_crazyflie = {path/to/nb.ipynb},      % or {}
  note           = {Brief description...}   % plain text
}
```

**Then run:**
```bash
python3 docs/generate_bib_metadata.py && cd docs && make html
```
