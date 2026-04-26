# Bibliography System Guide

This guide explains how to use the searchable, filterable bibliography system in dynamicalnodes documentation.

## Overview

The bibliography system allows you to:
- Maintain a BibTeX file of papers whose algorithms you implement
- Add custom metadata fields for filtering (category, observability, robot platform, etc.)
- Display a searchable bibliography page with interactive filters on ReadTheDocs
- Link to papers from anywhere in the documentation using citations

## Files Structure

```
docs/source/
├── references.bib           # BibTeX file with all papers
├── bibliography.rst         # Bibliography page with filters
├── _static/
│   ├── css/
│   │   └── bibliography.css # Styling for filters and entries
│   └── js/
│       └── bibliography.js  # JavaScript for interactive filtering
└── conf.py                  # Sphinx configuration (already configured)
```

## Adding New Papers

### 1. Add Entry to references.bib

Add a new BibTeX entry with custom fields:

```bibtex
@article{smith2023control,
  title={Advanced Control for Quadrotors},
  author={Smith, John and Doe, Jane},
  journal={Robotics Journal},
  volume={10},
  number={3},
  pages={45--60},
  year={2023},
  url={https://arxiv.org/abs/2301.12345},
  keywords={control, trajectory-planning},
  dynamicalnodes_category={mpc},
  dynamicalnodes_observability={full},
  dynamicalnodes_robot={crazyflie},
  dynamicalnodes_implemented={planned},
  note={MPC controller for Crazyflie. Implementation planned for v0.3}
}
```

### 2. Custom Fields Explained

**Required Standard Fields:**
- `title`, `author`, `year`, `journal`/`booktitle`
- `url`: Link to arXiv or DOI (highly recommended)

**Custom dynamicalnodes Fields:**

- **keywords**: Broad categories (comma-separated)
  - Options: `state-estimation`, `control`, `planning`, `filtering`, etc.

- **dynamicalnodes_category**: Specific algorithm type
  - Options: `kalman-filter`, `pid`, `mpc`, `lqr`, `ekf`, `ukf`, etc.

- **dynamicalnodes_observability**: State observability requirement
  - Options: `full`, `partial`

- **dynamicalnodes_robot**: Target robot platform
  - Options: `turtlebot`, `crazyflie`, `generic`, or custom robot names

- **dynamicalnodes_implemented**: Implementation status
  - Options: `yes`, `planned`, `no`

- **note**: Brief description and implementation details
  - Mention the dynamicalnodes module path if implemented
  - Mention planned version if not yet implemented

### 3. Filter Options

Update the filter dropdowns in `bibliography.rst` if you add new categories:

```rst
<select id="algorithm-filter" class="filter-select">
  <option value="all">All</option>
  <option value="kalman-filter">Kalman Filter</option>
  <option value="pid">PID</option>
  <option value="mpc">MPC</option>
  <option value="your-new-category">Your New Category</option>
</select>
```

## Citing Papers in Documentation

### In reStructuredText (.rst files)

```rst
According to the seminal work by :cite:`kalman1960new`, the Kalman filter
provides optimal estimates for linear systems.

The UKF :cite:`julier1997new` extends this to nonlinear systems.

Multiple citations can be used together :cite:`kalman1960new,julier1997new`.
```

### In Markdown files (.md files with MyST parser)

```markdown
According to {cite}`kalman1960new`, the Kalman filter is optimal.

Multiple citations: {cite}`kalman1960new,julier1997new`.
```

## How the Filtering Works

1. **On Page Load**: JavaScript (`bibliography.js`) extracts metadata from each bibliography entry
2. **User Interaction**: When filters are changed, entries are shown/hidden based on metadata
3. **Visual Feedback**: Implemented papers have a green border, planned papers have yellow
4. **Badges**: Implementation status badges are automatically added to entries

## Customization

### Adding New Filter Categories

1. Add the custom field to your BibTeX entries
2. Add a new filter dropdown in `bibliography.rst`
3. Update `bibliography.js` to handle the new filter:

```javascript
const newFilter = document.getElementById('new-filter');

// In applyFilters():
if (visible && newFilterValue !== 'all') {
    const newField = citation.dataset.newField || '';
    if (!newField.includes(newFilterValue)) {
        visible = false;
    }
}

// In initializeCitations():
const newField = extractField(text, 'dynamicalnodes_newfield') || '';
citation.dataset.newField = newField;
```

### Styling Changes

Edit `_static/css/bibliography.css` to customize:
- Filter appearance
- Entry highlighting
- Badge colors
- Responsive behavior

## Building the Documentation

```bash
cd docs
make clean
make html
```

The bibliography will be available at `build/html/bibliography.html`

## Testing on ReadTheDocs

The bibliography system works automatically on ReadTheDocs because:
1. `sphinxcontrib-bibtex` is in your `docs` dependencies (pyproject.toml)
2. Custom CSS/JS files are included via `html_css_files` and `html_js_files` in conf.py
3. The `_static` directory is configured as a static path

## Example Workflow

1. Find a paper you want to implement
2. Add it to `references.bib` with appropriate metadata
3. Set `dynamicalnodes_implemented=no` or `dynamicalnodes_implemented=planned`
4. When you implement it, update `dynamicalnodes_implemented=yes` and add the module path to the note
5. Cite it in your documentation pages
6. Users can filter to see all implemented algorithms for their robot!

## Tips

- Use consistent naming for `dynamicalnodes_category` values (e.g., always use "kalman-filter" not "kf" or "Kalman")
- Keep `dynamicalnodes_robot=generic` for algorithms that work on any platform
- Link to arXiv when possible (free, stable, accessible)
- Use the `note` field to help users find the implementation in your codebase
- Add version numbers to planned implementations so users know when to expect them
