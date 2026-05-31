Installation
============

We **highly recommend** you install things using the Docker environment below to avoid any conflicts with existing ros installations you might have on your local machine. Once you've played around with the theory-to-ros pipeline and determined it fits your use case, then you may want to consider installing things locally for the computational benefits.

Docker (ROS2 + PlotJuggler)
----------------------------

A Docker image is provided that bundles dynamicalnodes, ROS2 Jazzy, and
`PlotJuggler <https://github.com/facontidavide/PlotJuggler>`_ for immediate use
without a local ROS2 install.

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

   jupyter lab --ip=0.0.0.0 --no-browser --allow-root

Then open your **host browser** at ``http://localhost:8888``. The port is
directly accessible because ``--network host`` is set.

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
require a working ROS2 installation (Jazzy Jalisco or later). Install ROS2 via the
`official instructions <https://docs.ros.org/en/jazzy/Installation.html>`_,
then install dynamicalnodes as above.

The core :class:`~dynamicalnodes.DynamicalSystem` class has no ROS2 dependency
and works anywhere Python runs.


