# Bibliography Workflow - Updated

## Quick Workflow

When you add or modify papers in the bibliography:

1. **Edit `docs/source/references.bib`** - Add your new paper with custom fields
2. **Run the generator**: `python3 docs/generate_bib_metadata.py`
3. **Build docs**: `cd docs && make html`
4. **Test** the filters in your browser

## Why This Approach?

sphinxcontrib.bibtex doesn't render custom BibTeX fields (like `dynamicalnodes_category`, `dynamicalnodes_robot`, etc.) in the HTML output. To make filtering work, we:

1. Store metadata in the `.bib` file (for easy maintenance)
2. Auto-generate a JavaScript file (`bib_metadata.js`) from the `.bib` file
3. Use JavaScript to match bibliography entries with metadata and apply filters

## Step-by-Step

### 1. Add a Paper to references.bib

```bibtex
@article{smith2024control,
  title        = {Advanced MPC for Quadrotors},
  author       = {Smith, John},
  journal      = {Robotics Journal},
  year         = {2024},
  url          = {https://arxiv.org/abs/2401.12345},
  keywords     = {control, trajectory-planning},
  dynamicalnodes_category = {mpc},
  dynamicalnodes_observability = {full},
  dynamicalnodes_robot  = {crazyflie},
  dynamicalnodes_implemented = {planned},
  note         = {MPC controller for Crazyflie quadrotor}
}
```

### 2. Generate Metadata

Run from the `docs/` directory:

```bash
python3 generate_bib_metadata.py
```

This creates/updates `docs/source/_static/js/bib_metadata.js`

### 3. Build Documentation

```bash
cd docs
source ../.venv/bin/activate
make html
```

### 4. Test

Open `docs/build/html/bibliography.html` and test the filters.

## How It Works

1. **`generate_bib_metadata.py`**: Parses `references.bib` and extracts custom fields into a JavaScript object
2. **`bib_metadata.js`**: Contains `PAPER_METADATA` object with all metadata
3. **`bibliography.js`**:
   - Matches HTML bibliography entries to metadata using author names and years
   - Adds data attributes to HTML elements
   - Filters based on these attributes
   - Shows/hides entries dynamically

## Automation (Optional)

Add this to your `docs/Makefile` to auto-generate metadata before building:

```makefile
html:
	python3 ../generate_bib_metadata.py
	@$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
```

Or create a pre-commit hook to run the generator automatically.

## Troubleshooting

**Filters not working after adding a paper:**
- Did you run `generate_bib_metadata.py`?
- Did you rebuild with `make html`?
- Check browser console for JavaScript errors

**Paper not appearing in filters:**
- Check that the BibTeX entry has all custom fields
- Verify the year and author name are in the BibTeX key (e.g., `smith2024control`)
- The matching heuristic uses year + author name from the key

**Wrong paper getting filtered:**
- Make sure BibTeX keys are unique and descriptive
- Use format: `authorYEARkeyword` (e.g., `kalman1960new`, `julier1997ukf`)

## Files Overview

```
docs/
├── generate_bib_metadata.py       # Run this when you update references.bib
├── source/
│   ├── references.bib              # Edit this to add papers
│   ├── bibliography.rst            # Filter UI (rarely needs changes)
│   └── _static/
│       ├── css/
│       │   └── bibliography.css    # Styling
│       └── js/
│           ├── bib_metadata.js     # AUTO-GENERATED - don't edit
│           └── bibliography.js     # Filter logic
```

## Remember

✅ **DO**: Run `generate_bib_metadata.py` after editing `references.bib`
❌ **DON'T**: Edit `bib_metadata.js` manually (it will be overwritten)
✅ **DO**: Use consistent BibTeX key format (`authorYEARkeyword`)
✅ **DO**: Include all custom fields for proper filtering
