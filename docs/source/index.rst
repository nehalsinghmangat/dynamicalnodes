dynamicalnodes
==============

**dynamicalnodes** is a Python framework for modeling control systems and deploying them as ROS2 nodes.

It follows a four-step pipeline: **Theory → Python → ROS2 → Hardware**.

Each component (plant, controller, estimator, reference generator) is modeled as a
:class:`~dynamicalnodes.DynamicalSystem` with a state transition function ``f`` and an
observation function ``h``. Components compose naturally by passing outputs of one
system as inputs to another.

.. toctree::
   :maxdepth: 1
   :caption: Getting Started

   installation

.. toctree::
   :maxdepth: 1
   :caption: Notebooks

   notebooks/algorithm_library
   notebooks/cruise_control

.. toctree::
   :maxdepth: 1
   :caption: API Reference

   api/index

.. toctree::
   :maxdepth: 1
   :caption: Legal

   license
