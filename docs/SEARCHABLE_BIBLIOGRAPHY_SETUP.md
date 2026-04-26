# Searchable Bibliography Setup - Complete Summary

This document summarizes the searchable, filterable bibliography system that has been set up for your dynamicalnodes documentation.

## What Was Done

### 1. Sphinx Configuration (`docs/source/conf.py`)
- Enabled `sphinxcontrib.bibtex` extension
- Configured to use `references.bib` as the bibliography file
- Added custom CSS and JavaScript files for interactive filtering
- Set bibliography style to author-year format

### 2. Bibliography File (`docs/source/references.bib`)
- Created with custom fields for filtering:
  - `keywords`: Broad categories (state-estimation, control, planning)
  - `dynamicalnodes_category`: Specific algorithm (kalman-filter, pid, mpc, etc.)
  - `dynamicalnodes_observability`: Full or partial state observability
  - `dynamicalnodes_robot`: Target platform (turtlebot, crazyflie, generic)
  - `dynamicalnodes_implemented`: Status (yes, planned, no)
- Includes template and two example entries (Kalman, UKF)

### 3. Bibliography Page (`docs/source/bibliography.rst`)
- Created interactive filter interface with 5 filter categories
- Includes "Reset Filters" button
- Shows "No results" message when filters exclude all papers
- Displays all bibliography entries with automatic numbering

### 4. Custom Styling (`docs/source/_static/css/bibliography.css`)
- Styled filter interface with modern, clean design
- Added visual indicators for implemented papers (green border)
- Added visual indicators for planned papers (yellow border)
- Responsive design for mobile devices
- Auto-generated badges showing implementation status

### 5. Interactive JavaScript (`docs/source/_static/js/bibliography.js`)
- Extracts metadata from bibliography entries on page load
- Filters entries in real-time based on user selections
- Adds implementation status badges to entries
- Shows/hides "no results" message appropriately
- Handles reset functionality

### 6. Documentation Updates
- Added bibliography page to main documentation index
- Created example page showing citation usage
- Added comprehensive usage guide (BIBLIOGRAPHY_GUIDE.md)

### 7. Dependencies
- Added `sphinxcontrib-bibtex>=2.5.0` to docs dependencies
- Added `sphinx-autodoc-typehints>=1.24.0` to docs dependencies

## How to Use

### Adding a New Paper

1. **Add to `docs/source/references.bib`:**

```bibtex
@article{yourpaper2024,
  title={Your Paper Title},
  author={Last, First and Another, Author},
  journal={Journal Name},
  year={2024},
  url={https://arxiv.org/abs/2401.12345},
  keywords={state-estimation, filtering},
  dynamicalnodes_category={kalman-filter},
  dynamicalnodes_observability={full},
  dynamicalnodes_robot={turtlebot},
  dynamicalnodes_implemented={yes},
  note={Implementation in dynamicalnodes.utilities.estimators.kf}
}
```

2. **Cite it in your documentation:**

```rst
The algorithm from :cite:`yourpaper2024` is implemented in dynamicalnodes.
```

3. **Rebuild docs:**

```bash
cd docs
make html
```

### Filter Categories Available

**Category** (from `keywords` field):
- state-estimation
- control
- planning
- filtering
- (add more as needed)

**Algorithm** (from `dynamicalnodes_category` field):
- kalman-filter
- pid
- mpc
- lqr
- (add more as needed)

**Observability** (from `dynamicalnodes_observability` field):
- full
- partial

**Robot Platform** (from `dynamicalnodes_robot` field):
- turtlebot
- crazyflie
- generic
- (add more as needed)

**Implementation Status** (from `dynamicalnodes_implemented` field):
- yes - Fully implemented
- planned - Implementation planned
- no - Not planned for implementation

## Features

### Visual Indicators
- ✅ **Green left border**: Implemented papers (`dynamicalnodes_implemented=yes`)
- 🟡 **Yellow left border**: Planned papers (`dynamicalnodes_implemented=planned`)
- 🏷️ **Badges**: Automatic "IMPLEMENTED" or "PLANNED" badges on entries

### Interactive Filtering
- Real-time filtering as you change selections
- Multiple filters work together (AND logic)
- "Reset Filters" button to clear all filters
- Shows helpful message when no papers match filters

### ReadTheDocs Integration
- Everything works automatically on ReadTheDocs
- No special configuration needed on RTD side
- All static files (CSS/JS) are properly included
- Bibliography builds with each documentation update

## File Structure

```
docs/
├── source/
│   ├── conf.py                    # Sphinx config (configured)
│   ├── index.rst                  # Main index (updated)
│   ├── references.bib             # BibTeX database (add papers here)
│   ├── bibliography.rst           # Bibliography page with filters
│   ├── using_citations_example.rst # Example (can delete)
│   └── _static/
│       ├── css/
│       │   └── bibliography.css   # Filter styling
│       └── js/
│           └── bibliography.js    # Interactive filtering
├── BIBLIOGRAPHY_GUIDE.md          # Detailed usage guide
└── SEARCHABLE_BIBLIOGRAPHY_SETUP.md # This file
```

## Next Steps

1. **Remove example papers** from `references.bib` (Kalman 1960, Julier 1997)
2. **Add your actual papers** with proper metadata
3. **Update filter options** in `bibliography.rst` if you add new categories
4. **Delete or repurpose** `using_citations_example.rst`
5. **Install the new dependency**:
   ```bash
   pip install -e ".[docs]"
   ```
6. **Build and test locally**:
   ```bash
   cd docs
   make clean
   make html
   open build/html/bibliography.html
   ```

## Testing

To test the system locally:

1. Install docs dependencies:
   ```bash
   pip install -e ".[docs]"
   ```

2. Build documentation:
   ```bash
   cd docs
   make html
   ```

3. Open in browser:
   ```bash
   # The bibliography page will be at:
   docs/build/html/bibliography.html
   ```

4. Test the filters by selecting different options
5. Verify that citations work in other pages

## Customization

### Adding New Filter Categories

If you want to add a new filter dimension (e.g., "Complexity: Linear/Nonlinear"):

1. Add the field to your BibTeX entries: `dynamicalnodes_complexity={linear}`
2. Add a filter dropdown in `bibliography.rst`
3. Update `bibliography.js` to extract and filter on this field
4. Update the usage guide

### Changing Styles

- Edit `_static/css/bibliography.css` for visual changes
- Colors, borders, badges, spacing can all be customized
- The CSS includes comments for common customization points

## Troubleshooting

**Bibliography not showing:**
- Check that `sphinxcontrib-bibtex` is installed
- Verify `references.bib` has valid BibTeX syntax
- Check Sphinx build output for errors

**Filters not working:**
- Open browser console (F12) to check for JavaScript errors
- Verify that `bibliography.js` is loaded
- Check that filter IDs match between RST and JavaScript

**Citations not resolving:**
- Make sure citation keys match exactly (case-sensitive)
- Rebuild documentation with `make clean && make html`
- Check that the paper is actually in `references.bib`

## Benefits

✅ Users can quickly find papers by algorithm type
✅ Users can see what's implemented vs. planned
✅ Users can filter to their specific robot platform
✅ Papers are searchable via RTD's built-in search
✅ Clean, professional presentation
✅ Easy to maintain (just edit BibTeX file)
✅ Automatic on ReadTheDocs, no special hosting needed

## Example Use Cases

1. **User wants to see all Kalman filter variants:**
   - Select "Algorithm: Kalman Filter"
   - See all EKF, UKF, KF papers

2. **User wants TurtleBot-specific algorithms:**
   - Select "Robot Platform: TurtleBot"
   - See only papers tested/implemented on TurtleBot

3. **User wants to know what's already implemented:**
   - Select "Implementation Status: Implemented"
   - See green-bordered entries with implementation paths

4. **Developer adding new feature:**
   - Check if algorithm is already in bibliography
   - If yes, update `dynamicalnodes_implemented` to `yes` and add note
   - If no, add paper to bibliography with proper metadata
