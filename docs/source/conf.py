# Configuration file for the Sphinx documentation builder.
import os
import sys

# -- Path setup --------------------------------------------------------------

# Add source directories to sys.path so autodoc can find modules
sys.path.insert(0, os.path.abspath("../../src"))

# -- Project information -----------------------------------------------------

project = "dynamicalnodes"
copyright = "2025, Nehal Singh Mangat"
author = "Nehal Singh Mangat"
release = "0.1.0"  # Version of the project

# -- General configuration ---------------------------------------------------

extensions = [
    "myst_nb",
    "sphinx.ext.autodoc",  # Automatically document docstrings
    "sphinx.ext.autosummary",  # Generate summary tables and toctrees for API docs
    "sphinx.ext.napoleon",  # Support for Google/NumPy-style docstrings
    "sphinx.ext.viewcode",  # Add [source] links to Python code
    "sphinx.ext.mathjax",  # Math rendering in HTML (LaTeX-style)
    "sphinx_autodoc_typehints",  # Show type hints in API docs
    "sphinx.ext.intersphinx",  # Link to external Sphinx docs (like NumPy)
    "sphinx_toolbox.collapse",  # Support for collapsible content blocks
    "sphinx.ext.graphviz",  # Render Graphviz diagrams in docs
    "sphinxcontrib.bibtex",  # Bibliography support
]

myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_image",
]
myst_url_schemes = ("http", "https", "mailto")

# Generate anchors for h1, h2, h3 headings (show ### in sidebar TOC)
myst_heading_anchors = 3

# Automatically add toctree entries for page sections (enables local TOC in sidebar)
myst_update_mathjax = False

# Notebook execution configuration
# "off" - never execute (use saved outputs only)
# "auto" - execute only if no outputs exist in .ipynb
# "cache" - execute and cache results, re-run only on code changes
# "force" - always execute on every build
#
# Individual notebooks can override this with mystnb.execution_mode metadata
nb_execution_mode = "cache"  # Execute and cache, re-run only on code changes

# Execution cache directory (stores execution results)
nb_execution_cache_path = ".jupyter_cache"

# Maximum execution time per cell (in seconds)
nb_execution_timeout = 300  # 5 minutes per cell

# Kernel to use for execution
nb_kernel_rgx_aliases = {"python3": "python3"}

# Cell execution configuration
nb_execution_excludepatterns = []  # Exclude specific notebooks from execution
nb_execution_raise_on_error = False  # Don't fail build on notebook errors

# Cell tag configuration
# These tags control cell behavior during build:
# - "hide-input": Hide the code cell input (keep output visible)
# - "hide-output": Hide the cell output (keep code visible)
# - "remove-cell": Remove the entire cell from output
# - "skip-execution": Don't execute this cell (use saved outputs)
nb_execution_show_tb = True  # Show full traceback on execution errors

# Render configuration for cell tags
nb_render_priority = {
    "html": (
        "application/vnd.jupyter.widget-view+json",
        "application/javascript",
        "text/html",
        "image/svg+xml",
        "image/png",
        "image/jpeg",
        "text/markdown",
        "text/latex",
        "text/plain",
    )
}


# Autodoc default behavior for documenting modules
autodoc_default_options = {
    "members": True,  # Include class/method/function members
    "undoc-members": True,  # Include members without docstrings
    "show-inheritance": True,  # Show class inheritance info
    "inherited-members": True,  # Show members inherited from base classes
}

autodoc_typehints = "description"  # Move type hints from signature into docstring

# Autosummary configuration
autosummary_generate = True  # Automatically generate stub files for autosummary
autosummary_imported_members = False  # Don't include imported members

# Napoleon (Google/NumPy docstring style) configuration
napoleon_google_docstring = True
napoleon_numpy_docstring = True

# BibTeX configuration
bibtex_bibfiles = ["references.bib"]
bibtex_default_style = "plain"
bibtex_reference_style = "author_year"


# Intersphinx mappings to other project documentation for :ref: cross-links
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
}

# Template and pattern configuration
templates_path = ["_templates"]  # Custom Jinja templates
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]  # Files to ignore

# -- HTML output configuration -----------------------------------------------

html_theme = "sphinx_rtd_theme"  # Theme used (ReadTheDocs theme)
html_static_path = ["_static"]  # Static assets like CSS/JS/images

# ReadTheDocs theme options
html_theme_options = {
    "navigation_depth": -1,  # Show ALL levels in sidebar (-1 = unlimited)
    "collapse_navigation": False,  # Keep navigation expanded
    "sticky_navigation": True,  # Keep sidebar visible while scrolling
    "includehidden": True,  # Show hidden toctrees in sidebar
    "titles_only": False,  # Show full navigation tree, not just titles
}

# Sphinx will generate local TOCs for each page showing internal sections
html_use_index = True
html_domain_indices = True

# Set the depth for local page TOC (shows h1, h2, h3 when on that specific page)
# This is separate from toctree maxdepth which controls global navigation
toc_object_entries_show_parents = 'hide'

# Custom CSS and JavaScript files
html_css_files = ["css/bibliography.css", "css/custom.css"]

html_js_files = [
    "js/bib_metadata.js",
    "js/bibliography.js",
]

# -- Math configuration ------------------------------------------------------

# Load MathJax from CDN for faster builds and modern features
mathjax_path = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"
imgmath_image_format = "svg"  # Preferred image format for math output
imgmath_use_preview = True  # Display math preview images if possible

# -- LaTeX output configuration ----------------------------------------------

latex_engine = "pdflatex"  # LaTeX engine; alternatives: 'xelatex', 'lualatex'

latex_elements = {
    "papersize": "letterpaper",  # U.S. paper size
    "pointsize": "11pt",  # Font size
    "figure_align": "H",  # Force figure placement using float
    "preamble": r"""
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{bm}
\usepackage{mathtools}
\usepackage{physics}
\usepackage{graphicx}
\usepackage{float}
\usepackage{etoolbox}
\usepackage{listings}
\lstset{
  basicstyle=\ttfamily,
  breaklines=true,
  columns=fullflexible
}
""",  # Extra LaTeX packages for math, code formatting, and layout
}

# -- EPUB output configuration -----------------------------------------------

epub_show_urls = "footnote"  # Where to show URLs in EPUB output (if built)
