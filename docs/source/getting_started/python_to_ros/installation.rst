:doc:`← Python to ROS <index>`

============
Installation
============


To use dynamicalnodes's ROS2 integration (``ROSNode``, message conversion, Gazebo simulation), you need ROS2 installed.

**Supported Configurations:**

* **Ubuntu 24.04 LTS** → ROS2 Jazzy Jalisco (recommended)
* **Ubuntu 22.04 LTS** → ROS2 Humble Hawksbill

.. note::
   ROS2 is optional. Core dynamicalnodes functionality (``DynamicalSystem``) works without ROS2. The ``ROSNode`` class and ROS utilities will only fail if actually used without ROS2 installed.

Ubuntu 24.04: ROS2 Jazzy Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Ensure UTF-8 locale
   locale
   sudo apt update && sudo apt install locales
   sudo locale-gen en_US en_US.UTF-8
   sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
   export LANG=en_US.UTF-8

   # Enable required repositories
   sudo apt install software-properties-common
   sudo add-apt-repository universe

   # Add ROS2 GPG key
   sudo apt update && sudo apt install curl -y
   sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
       -o /usr/share/keyrings/ros-archive-keyring.gpg

   # Add ROS2 repository
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
       | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

   # Install ROS2 Jazzy Desktop
   sudo apt update
   sudo apt upgrade
   sudo apt install ros-jazzy-desktop

   # Install development tools
   sudo apt install ros-dev-tools

   # Source ROS2 setup (add this to ~/.bashrc for persistence)
   source /opt/ros/jazzy/setup.bash

   # Install Python ROS2 dependencies
   pip install rclpy

Ubuntu 22.04: ROS2 Humble Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Ensure UTF-8 locale
   locale
   sudo apt update && sudo apt install locales
   sudo locale-gen en_US en_US.UTF-8
   sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
   export LANG=en_US.UTF-8

   # Enable required repositories
   sudo apt install software-properties-common
   sudo add-apt-repository universe

   # Add ROS2 GPG key
   sudo apt update && sudo apt install curl -y
   sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
       -o /usr/share/keyrings/ros-archive-keyring.gpg

   # Add ROS2 repository
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
       | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

   # Install ROS2 Humble Desktop
   sudo apt update
   sudo apt upgrade
   sudo apt install ros-humble-desktop

   # Install development tools
   sudo apt install ros-dev-tools

   # Source ROS2 setup (add this to ~/.bashrc for persistence)
   source /opt/ros/humble/setup.bash

   # Install Python ROS2 dependencies
   pip install rclpy

Make ROS2 Sourcing Permanent
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add the ROS2 setup to your ``~/.bashrc`` to automatically source it in new terminals:

.. code-block:: bash

   # For ROS2 Jazzy (Ubuntu 24.04)
   echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc

   # OR for ROS2 Humble (Ubuntu 22.04)
   echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc

   # Reload your shell configuration
   source ~/.bashrc

:doc:`← Python to ROS <index>`
