Contributing to the Algorithm Library
=====================================

The algorithm library is ...

1. ***Add the paper** to ``references.bib``
2. **Implement the algorithm** in dynamicalnodes (as DynamicalSystem-compatible functions)
3. **Create implementation notebooks** showing usage in dynamicalnodes, TurtleBot, and/or Crazyflie
4. **Update metadata** so your implementation appears in the Algorithm Library

Step 1: Add Your Paper to references.bib
=========================================

Location: ``docs/source/references.bib``

Add a BibTeX entry for your algorithm's paper with these required and optional fields:

Required Fields
---------------

- **title**: Paper title
- **author**: Author(s) name(s)
- **year**: Publication year
- **keywords**: Must be either ``"estimation"`` or ``"control"``

Optional Fields
---------------

- **journal/booktitle**: Publication venue
- **volume, number, pages**: Citation details
- **publisher**: Publisher name
- **url**: DOI or paper URL
- **impl_dynamicalnodes**: Path to dynamicalnodes implementation notebook (e.g., ``"notebooks/my_algorithm.ipynb"``)
- **impl_turtlebot**: Path to TurtleBot implementation notebook
- **impl_crazyflie**: Path to Crazyflie implementation notebook
- **note**: Brief description of the algorithm and implementations

Template
--------

.. code-block:: bibtex

   @article{author2024algorithm,
     title        = {Novel Control Algorithm for Robotics},
     author       = {Author, First and Author, Second},
     journal      = {IEEE Transactions on Robotics},
     volume       = {40},
     number       = {2},
     pages        = {123--145},
     year         = {2024},
     publisher    = {IEEE},
     url          = {https://doi.org/10.1109/example},
     keywords     = {control},
     impl_dynamicalnodes   = {notebooks/my_algorithm_dynamicalnodes.ipynb},
     impl_turtlebot = {notebooks/my_algorithm_turtlebot.ipynb},
     impl_crazyflie = {notebooks/my_algorithm_crazyflie.ipynb},
     note         = {Brief description of what this algorithm does}
   }

Example
-------

.. code-block:: bibtex

   @article{kalman1960new,
     title        = {A new approach to linear filtering and prediction problems},
     author       = {Kalman, Rudolph Emil},
     journal      = {Journal of Basic Engineering},
     volume       = {82},
     number       = {1},
     pages        = {35--45},
     year         = {1960},
     publisher    = {American Society of Mechanical Engineers},
     url          = {https://doi.org/10.1115/1.3662552},
     keywords     = {estimation},
     impl_dynamicalnodes   = {notebooks/algorithm_library/kf_dynamicalnodes.ipynb},
     impl_turtlebot = {notebooks/turtlebot_kf_demo.ipynb},
     impl_crazyflie = {notebooks/crazyflie_kf_demo.ipynb},
     note         = {Classic Kalman filter paper}
   }

Step 2: Implement the Algorithm in dynamicalnodes
=========================================

Location: ``src/dynamicalnodes/algorithm_library/``

Algorithms are organized by category:

- **Estimators**: ``src/dynamicalnodes/algorithm_library/estimators/``
- **Controllers**: ``src/dynamicalnodes/algorithm_library/controllers/``

Implementation Guidelines
-------------------------

1. **Create a new module** (e.g., ``my_algorithm.py``) in the appropriate category directory

2. **Implement as DynamicalSystem-compatible functions**:

   - Define ``f()`` for state evolution
   - Define ``h()`` for observation/output
   - Use the ``_smart_call()`` pattern for flexible parameter binding

3. **Follow dynamicalnodes conventions**:

   - Functions should be pure (no side effects)
   - Accept parameters via dictionary
   - Return NumPy arrays
   - Include comprehensive docstrings with examples

4. **Add doctests** to demonstrate usage:

   .. code-block:: python

      def my_algorithm_f(x, param_dict):
          """
          State evolution function for my algorithm.

          Parameters
          ----------
          x : np.ndarray
              Current state
          param_dict : dict
              Dictionary containing algorithm parameters

          Returns
          -------
          x_next : np.ndarray
              Next state

          Examples
          --------
          >>> import numpy as np
          >>> x = np.array([1.0, 2.0])
          >>> params = {'dt': 0.1, 'gain': 0.5}
          >>> x_next = my_algorithm_f(x, params)
          """
          # Implementation here
          pass

5. **Export in __init__.py**:

   .. code-block:: python

      # In src/dynamicalnodes/algorithm_library/controllers/__init__.py
      from . import my_algorithm

      __all__ = ["pid", "my_algorithm"]

Example Structure
-----------------

.. code-block:: python

   # src/dynamicalnodes/algorithm_library/controllers/my_algorithm.py
   import numpy as np
   from dynamicalnodes import DynamicalSystem

   class MyAlgorithm:
       """Implementation of My Algorithm (Author, Year)."""

       @staticmethod
       def f(state, param_dict):
           """State evolution function."""
           # Extract parameters
           dt = param_dict.get('dt', 0.01)
           gain = param_dict.get('gain', 1.0)

           # Compute next state
           state_next = state + gain * dt
           return state_next

       @staticmethod
       def h(state, param_dict):
           """Output function."""
           return state

Step 3: Create Implementation Notebooks
========================================

Location: ``docs/source/notebooks/``

Create Jupyter notebooks demonstrating your algorithm:

1. **dynamicalnodes implementation** (``my_algorithm_dynamicalnodes.ipynb``):

   - Pure software demonstration
   - Use synthetic data or simple examples
   - Show how to use your algorithm with ``DynamicalSystem``

2. **TurtleBot implementation** (``my_algorithm_turtlebot.ipynb``):

   - Deploy algorithm as ROS2 nodes
   - Show Gazebo simulation if applicable
   - Include real hardware deployment if possible

3. **Crazyflie implementation** (``my_algorithm_crazyflie.ipynb``):

   - Deploy algorithm on Crazyflie drone
   - Show both simulation and real flight tests

Notebook Structure
------------------

Each notebook should include:

.. code-block:: markdown

   # Algorithm Name Implementation

   ## Introduction
   Brief description of the algorithm and its use case

   ## Theory
   Mathematical formulation (reference the paper)

   ## Implementation in dynamicalnodes
   Code showing how to use the algorithm

   ## Results
   Plots and analysis showing the algorithm working

   ## References
   Citation to the original paper

Notebook Template
-----------------

.. code-block:: python

   # Cell 1: Imports
   import numpy as np
   import matplotlib.pyplot as plt
   from dynamicalnodes import DynamicalSystem
   from dynamicalnodes.algorithm_library.controllers import my_algorithm

   # Cell 2: Setup
   # Define parameters, initial conditions, etc.

   # Cell 3: Create DynamicalSystem
   system = DynamicalSystem(
       f=my_algorithm.MyAlgorithm.f,
       h=my_algorithm.MyAlgorithm.h,
       param_dict={'dt': 0.01, 'gain': 1.0},
       state_name='my_state'
   )

   # Cell 4: Run simulation
   # Execute and collect results

   # Cell 5: Visualize
   # Plot results

Step 4: Update Metadata and Regenerate
=======================================

After creating your notebooks:

1. **Ensure notebook paths in references.bib are correct**:

   .. code-block:: bibtex

      impl_dynamicalnodes   = {notebooks/my_algorithm_dynamicalnodes.ipynb},
      impl_turtlebot = {notebooks/my_algorithm_turtlebot.ipynb},

   Note: Paths are relative to ``docs/source/``

2. **Regenerate bibliography metadata**:

   .. code-block:: bash

      cd docs
      python3 generate_bib_metadata.py

   This updates ``docs/source/_static/js/bib_metadata.js`` with your new implementation.

3. **Build documentation**:

   .. code-block:: bash

      cd docs
      make html

4. **Verify in browser**:

   Open ``docs/build/html/index.html`` and check that:

   - Your paper appears in the Algorithm Library
   - Category filter works correctly
   - Implementation circles are clickable and link to your notebooks

Testing Your Contribution
==========================

Before submitting:

1. **Run doctests**:

   .. code-block:: bash

      pytest --doctest-modules src/dynamicalnodes/algorithm_library/

2. **Test notebooks**:

   - Execute all cells in each notebook
   - Verify plots and outputs are correct
   - Check that imports work with the new API

3. **Build and check documentation**:

   .. code-block:: bash

      cd docs
      make clean
      make html

4. **Verify bibliography filtering**:

   - Check that your paper appears
   - Test category and implementation filters
   - Verify links to notebooks work

Submitting Your Contribution
=============================

1. Fork the dynamicalnodes repository on GitHub
2. Create a feature branch (``git checkout -b add-my-algorithm``)
3. Add your implementation files
4. Commit changes with descriptive messages
5. Push to your fork
6. Open a Pull Request with:

   - Description of the algorithm
   - Link to the original paper
   - Summary of implementations (dynamicalnodes/TurtleBot/Crazyflie)
   - Any testing you performed

Questions or Issues?
====================

- Open an issue on `GitHub <https://github.com/nehalsinghmangat/dynamicalnodes/issues>`_
- Check existing documentation and examples
- Review the Kalman filter implementation as a reference

Thank you for contributing to dynamicalnodes!
