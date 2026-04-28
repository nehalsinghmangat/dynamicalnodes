Installation
============

Requirements
------------

Python 3.12 or later.

Install
-------

.. code-block:: bash

   pip install dynamicalnodes

For development:

.. code-block:: bash

   git clone https://github.com/nehalsinghmangat/dynamicalnodes
   cd dynamicalnodes
   pip install -e ".[dev]"

ROS2 Integration
----------------

ROS2-dependent features (:class:`~dynamicalnodes.ROSNode`, :mod:`~dynamicalnodes.rostools`)
require a working ROS2 installation (Humble or later). Install ROS2 via the
`official instructions <https://docs.ros.org/en/humble/Installation.html>`_,
then install dynamicalnodes as above.

The core :class:`~dynamicalnodes.DynamicalSystem` class has no ROS2 dependency
and works anywhere Python runs.
