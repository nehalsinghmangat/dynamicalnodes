:doc:`← Getting Started <../index>`

============
Installation
============


For robot simulation capabilities, install Gazebo. The version depends on your ROS2 distribution.

Gazebo Harmonic (for ROS2 Jazzy on Ubuntu 24.04)
================================================

.. code-block:: bash

   # Install Gazebo Harmonic
   sudo apt update
   sudo apt install ros-jazzy-ros-gz

   # Verify installation
   gz sim --version

Gazebo Garden (for ROS2 Humble on Ubuntu 22.04)
===============================================

.. code-block:: bash

   # Install Gazebo Garden
   sudo apt update
   sudo apt install ros-humble-ros-gz

   # Verify installation
   gz sim --version

Install Robot-Specific Packages
===============================

For TurtleBot3 simulation:

.. code-block:: bash

   # For ROS2 Jazzy
   sudo apt install ros-jazzy-turtlebot3*

   # For ROS2 Humble
   sudo apt install ros-humble-turtlebot3*

   # Set default TurtleBot3 model (add to ~/.bashrc)
   echo "export TURTLEBOT3_MODEL=burger" >> ~/.bashrc
   source ~/.bashrc

For Crazyflie simulation:

.. code-block:: bash

   # Install Crazyflie ROS2 packages
   # (Instructions vary by ROS2 version - consult Crazyflie documentation)
   sudo apt install ros-${ROS_DISTRO}-crazyflie*

Development Installation
-------------------------

For contributing to dynamicalnodes or running tests:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/nehalsinghmangat/dynamicalnodes.git
   cd dynamicalnodes

   # Create and activate virtual environment
   python3 -m venv .venv
   source .venv/bin/activate

   # Install in editable mode with dev dependencies
   pip install -e ".[dev]"

   # Run tests to verify installation
   pytest

   # Optional: Install pre-commit hooks
   pre-commit install

Documentation Build Setup
--------------------------

To build the documentation locally:

.. code-block:: bash

   # Install with documentation dependencies
   pip install -e ".[docs]"

   # Build documentation
   cd docs
   make html

   # View documentation (open in browser)
   xdg-open build/html/index.html  # Linux
   # or
   open build/html/index.html      # macOS

Verification
------------

Verify your installation with these quick tests:

.. code-block:: bash

   # Test core functionality
   python -c "from dynamicalnodes import DynamicalSystem; print('✓ Core dynamicalnodes works')"

   # Test ROS2 integration (only if ROS2 installed)
   python -c "from dynamicalnodes import ROSNode; print('✓ ROS2 integration works')"

   # Test Gazebo utilities (only if ROS2 installed)
   python -c "from dynamicalnodes.gazebo import start_gazebo, stop_gazebo; print('✓ Gazebo utilities work')"

   # Test Kalman filter
   python -c "from dynamicalnodes.estimators import KF; print('✓ Estimators work')"

Troubleshooting
---------------

**ImportError: No module named 'rclpy'**

ROS2 is not installed or not sourced. Either:

1. Install ROS2 (see ROS2 Installation section)
2. Source ROS2 setup: ``source /opt/ros/<distro>/setup.bash``
3. Only use core dynamicalnodes features (avoid ``ROSNode``)

**Python version too old**

.. code-block:: bash

   # Check Python version
   python3 --version

   # Should show Python 3.12.x or higher
   # If not, install Python 3.12+

**Gazebo fails to launch**

.. code-block:: bash

   # Ensure Gazebo is installed
   gz sim --version

   # Check ROS-Gazebo bridge is installed
   ros2 pkg list | grep ros_gz

   # Verify robot packages
   ros2 pkg list | grep turtlebot3

**Virtual environment issues**

.. code-block:: bash

   # Deactivate current environment
   deactivate

   # Remove old environment
   rm -rf dynamicalnodes-env

   # Create fresh environment
   python3 -m venv dynamicalnodes-env
   source dynamicalnodes-env/bin/activate
   pip install --upgrade pip
   pip install dynamicalnodes

**Tests fail after development installation**

.. code-block:: bash

   # Ensure all dev dependencies are installed
   pip install -e ".[dev]"

   # Update pytest
   pip install --upgrade pytest pytest-doctestplus

   # Run with verbose output
   pytest -v

:doc:`← Getting Started <../index>`
