import os
import sys

sys.path.insert(0, os.path.abspath("../../src"))

project = "dynamicalnodes"
copyright = "2025, Nehal Singh Mangat"
author = "Nehal Singh Mangat"
release = "0.1"

extensions = [
    "myst_nb",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.mathjax",
    "sphinx_autodoc_typehints",
    "sphinx_copybutton",
]

myst_enable_extensions = ["dollarmath", "amsmath"]
myst_heading_anchors = 3

nb_execution_mode = "off"
nb_download_button = True

autodoc_mock_imports = [
    "rclpy",
    "rclpy.node",
    "rclpy.executors",
    "rclpy.qos",
    "rclpy.callback_groups",
    "rclpy.time",
    "builtin_interfaces",
    "builtin_interfaces.msg",
    "geometry_msgs",
    "geometry_msgs.msg",
    "nav_msgs",
    "nav_msgs.msg",
    "sensor_msgs",
    "sensor_msgs.msg",
    "std_msgs",
    "std_msgs.msg",
    "turtlesim",
    "turtlesim.msg",
]

autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}
autodoc_typehints = "description"
napoleon_numpy_docstring = True
napoleon_google_docstring = False

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_css_files = ["css/custom.css"]

html_theme_options = {
    "navigation_depth": 4,
    "collapse_navigation": False,
    "sticky_navigation": True,
}

mathjax_path = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"
