Installation
============

We **highly recommend** you install things using the Docker environment below to avoid any conflicts with existing ros installations you might have on your local machine. Once you've played around with the theory-to-ros pipeline and determined it fits your use case, then you may want to consider installing things locally for the computational benefits.

Docker (ROS2 + PlotJuggler)
----------------------------

A Docker image is provided that bundles dynamicalnodes, ROS2 Jazzy, and
`PlotJuggler <https://github.com/facontidavide/PlotJuggler>`_ for immediate use
without a local ROS2 install.

**Prerequisites:** Docker and Docker Compose. On Ubuntu:

.. code-block:: bash

   # Add Docker's official GPG key and repository
   sudo apt-get update
   sudo apt-get install -y ca-certificates curl
   sudo install -m 0755 -d /etc/apt/keyrings
   sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
   sudo chmod a+r /etc/apt/keyrings/docker.asc
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

   # Install Docker Engine and the Compose plugin
   sudo apt-get update
   sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

Allow the container to access your display (required for PlotJuggler):

.. code-block:: bash

   xhost +local:docker

Clone the repo and start the container in the background:

.. code-block:: bash

   git clone https://github.com/nehalsinghmangat/dynamicalnodes
   cd dynamicalnodes
   sudo docker compose up --build -d

Open a shell inside the running container:

.. code-block:: bash

   sudo docker compose exec dynamicalnodes bash

ROS2 is sourced automatically. You can immediately run:

.. code-block:: bash

   ros2 topic list
   plotjuggler
   python3 -c "import dynamicalnodes; print('ok')"

**GUI on macOS:** Install `XQuartz <https://www.xquartz.org/>`_, then before
starting the container set:

.. code-block:: bash

   export DISPLAY=host.docker.internal:0

**ROS2 node discovery:** ``network_mode: host`` is set in ``docker-compose.yml``,
which enables full DDS multicast across your network. This works on Linux. On
macOS and Windows (Docker Desktop), host networking behaves differently and
cross-host node discovery may be limited.

**JupyterLab inside the container:**

JupyterLab runs as a web server — no X11 or display forwarding required. Start
it inside the container:

.. code-block:: bash

   jupyter lab --ip=0.0.0.0 --no-browser --allow-root

Then open your **host browser** at ``http://localhost:8888``. Copy the token
from the terminal output when prompted. Because ``network_mode: host`` is set,
port 8888 on the container is directly accessible on your machine with no
additional port mapping needed.

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


