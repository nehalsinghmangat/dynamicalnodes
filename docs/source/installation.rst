Installation
============

Two paths are available: local installation or Docker. Local gives better
performance once you know the stack fits your use case. Docker is the faster
way to get started with no risk of conflicting with an existing ROS2 install.

Local Installation
------------------

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

Docker (ROS2 + PlotJuggler)
----------------------------

A Docker image is provided that bundles dynamicalnodes, ROS2 Jazzy, and
`PlotJuggler <https://github.com/facontidavide/PlotJuggler>`_ for immediate use
without a local ROS2 install.

We **highly recommend** starting here to avoid conflicts with any existing ROS2
installation on your machine.

**Prerequisites:** Docker. On Ubuntu / Linux Mint:

.. code-block:: bash

   # Add Docker's official GPG key and repository
   sudo apt-get update
   sudo apt-get install -y ca-certificates curl
   sudo install -m 0755 -d /etc/apt/keyrings
   sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
   sudo chmod a+r /etc/apt/keyrings/docker.asc
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

   # Install Docker Engine
   sudo apt-get update
   sudo apt-get install -y docker-ce docker-ce-cli containerd.io

Allow the container to access your display (required for PlotJuggler):

.. code-block:: bash

   xhost +local:docker

Clone the repo and build the image:

.. code-block:: bash

   git clone https://github.com/nehalsinghmangat/dynamicalnodes
   cd dynamicalnodes
   sudo docker build -t dynamicalnodes .

Run the container:

.. code-block:: bash

   sudo docker run -it --env DISPLAY=$DISPLAY --volume /tmp/.X11-unix:/tmp/.X11-unix --volume $(pwd):/ws/dynamicalnodes --network host dynamicalnodes

ROS2 is sourced automatically. You can immediately run:

.. code-block:: bash

   ros2 topic list
   ros2 run plotjuggler plotjuggler
   python3 -c "import dynamicalnodes; print('ok')"

**JupyterLab inside the container:**

JupyterLab runs as a web server — no X11 or display forwarding required. Start
it inside the container:

.. code-block:: bash

   jupyter lab --ip=0.0.0.0 --no-browser --allow-root --ServerApp.token='' --ServerApp.password=''

Then open your **host browser** at ``http://localhost:8888`` — no login required.
