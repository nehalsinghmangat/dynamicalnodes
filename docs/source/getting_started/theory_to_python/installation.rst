:doc:`← Theory to Python <index>`

==============
 Installation
==============

This guide provides step-by-step installation instructions for **dynamicalnodes**.

Prerequisites
-------------

**dynamicalnodes** requires:

* **Python 3.12 or higher**
* **pip** (Python package installer)
* **Linux** (recommended for ROS2 integration; deviate at your peril)


Basic Install
-------------

Install via pip:

.. code-block:: bash

   pip install dynamicalnodes

We **strongly recommend** using a virtual environment. Using a virtual environment isolates dynamicalnodes dependencies from your system Python:

.. code-block:: bash

   # Create a new virtual environment
   python3 -m venv dynamicalnodes-env

   # Activate the virtual environment
   source dynamicalnodes-env/bin/activate

   # Install dynamicalnodes
   pip install dynamicalnodes

   # Verify installation
   pip list | grep dynamicalnodes

To deactivate the virtual environment later:

.. code-block:: bash

   deactivate
   
:doc:`← Theory to Python <index>`

