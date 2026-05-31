Installation
============

We **highly recommend** you install things using the Docker environment below to avoid any conflicts with existing ros installations you might have on your local machine. Once you've played around with the theory-to-ros pipeline and determined it fits your use case, then you may want to consider installing things locally for the computational benefits.

Docker (ROS2 + PlotJuggler)
----------------------------

A Docker image is provided that bundles dynamicalnodes, ROS2 Jazzy, and
`PlotJuggler <https://github.com/facontidavide/PlotJuggler>`_ for immediate use
without a local ROS2 install.

**Prerequisites:** `Docker <https://docs.docker.com/get-docker/>`_ and
`Docker Compose <https://docs.docker.com/compose/install/>`_.

Build and start the container:

.. code-block:: bash

   git clone https://github.com/nehalsinghmangat/dynamicalnodes
   cd dynamicalnodes
   docker compose up --build

To open a shell inside the running container:

.. code-block:: bash

   docker compose exec dynamicalnodes bash

ROS2 is sourced automatically. You can immediately run:

.. code-block:: bash

   ros2 topic list
   plotjuggler
   python3 -c "import dynamicalnodes; print('ok')"

**GUI (PlotJuggler) on Linux:** Allow the container to access your display before
starting the container:

.. code-block:: bash

   xhost +local:docker

**GUI on macOS:** Install `XQuartz <https://www.xquartz.org/>`_, then set:

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


