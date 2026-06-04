Installation
============

**1. dynamicalnodes**

Requires Python 3.12 or later. A virtual environment is recommended to keep
dependencies isolated:

.. code-block:: bash

   python3 -m venv --system-site-packages .venv
   source .venv/bin/activate

``--system-site-packages`` makes ROS2 Python packages (``rclpy``, message
types, etc.) visible inside the venv without reinstalling them.

Then install dynamicalnodes:

.. code-block:: bash

   pip install dynamicalnodes

For development:

.. code-block:: bash

   git clone https://github.com/nehalsinghmangat/dynamicalnodes
   cd dynamicalnodes
   python3 -m venv --system-site-packages .venv
   source .venv/bin/activate
   pip install -e ".[dev]"

To reactivate the venv in a new terminal:

.. code-block:: bash

   source /path/to/dynamicalnodes/.venv/bin/activate

**2. ROS2 Jazzy**

Follow the `official ROS2 Jazzy installation instructions
<https://docs.ros.org/en/jazzy/Installation.html>`_ for your platform, then
source the setup file in every new terminal (or add it to ``~/.bashrc``):

.. code-block:: bash

   source /opt/ros/jazzy/setup.bash

Verify the correct version is active:

.. code-block:: bash

   printenv ROS_DISTRO   # should print: jazzy
   ros2 --version

If ``ROS_DISTRO`` is empty, ROS2 is not sourced in the current shell. If it
prints a different distro (e.g. ``humble``), another ROS2 version is sourced
instead. Only one distro can be active per shell — source the one you want
explicitly:

.. code-block:: bash

   source /opt/ros/jazzy/setup.bash   # overrides whatever was sourced before

To make Jazzy the default in every new terminal, add this line to ``~/.bashrc``
(replacing any existing ``source /opt/ros/.../setup.bash`` line):

.. code-block:: bash

   echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc

**3. PlotJuggler**

.. code-block:: bash

   sudo apt-get install -y ros-jazzy-plotjuggler-ros

Launch it:

.. code-block:: bash

   ros2 run plotjuggler plotjuggler
