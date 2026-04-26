:doc:`← ROS to Gazebo <index>`

==============================
Troubleshooting Gazebo Issues
==============================

This guide covers common issues when working with Gazebo simulations in ``dynamicalnodes``, along with their solutions.

.. contents:: Quick Navigation
   :local:
   :depth: 2

Gazebo Launcher Issues
=======================

Gazebo Won't Start
------------------

**Problem**: ``start_gazebo()`` hangs or fails with no output.

**Symptoms**:

.. code-block:: python

   gz = start_gazebo(robot='turtlebot3')
   # Hangs indefinitely or crashes

**Common Causes**:

1. **Missing ROS2 Gazebo packages**

   .. code-block:: bash

      # Check if packages installed
      ros2 pkg list | grep turtlebot3
      ros2 pkg list | grep gazebo

      # Install missing packages
      sudo apt install ros-humble-turtlebot3-gazebo
      sudo apt install ros-humble-gazebo-ros-pkgs

2. **GAZEBO_MODEL_PATH not set**

   .. code-block:: bash

      # Check environment
      echo $GAZEBO_MODEL_PATH

      # Fix: Source ROS2 workspace
      source /opt/ros/humble/setup.bash

3. **Conflicting Gazebo processes**

   .. code-block:: bash

      # Kill existing Gazebo processes
      pkill -9 gzserver
      pkill -9 gzclient
      pkill -9 'gz sim'

**Solution**: Install required packages, source ROS2 environment, clean up processes.

Gazebo Crashes with Graphics Error
-----------------------------------

**Problem**: Gazebo crashes immediately with OpenGL/graphics error.

**Error**:

.. code-block:: text

   libGL error: failed to load driver: swrast
   libGL error: MESA-LOADER: failed to open iris

**Cause**: Missing graphics drivers or running in headless environment (SSH, Docker, CI/CD).

**Solutions**:

1. **Use headless mode** (recommended for servers/notebooks):

   .. code-block:: python

      gz = start_gazebo(
          robot='turtlebot3',
          headless=True  # No GUI needed!
      )

2. **Install graphics drivers** (if GUI needed):

   .. code-block:: bash

      sudo apt install mesa-utils libgl1-mesa-glx

      # Test OpenGL support
      glxinfo | grep "OpenGL version"

3. **Use software rendering** (slower but works):

   .. code-block:: bash

      export LIBGL_ALWAYS_SOFTWARE=1

**Solution**: Use ``headless=True`` for most workflows. Only use GUI for visual debugging.

"Model not found" Error
------------------------

**Problem**:

.. code-block:: text

   Error: Unable to find model[turtlebot3_burger]

**Cause**: Gazebo cannot locate the robot model files.

**Solutions**:

1. **Check model path**:

   .. code-block:: bash

      echo $GAZEBO_MODEL_PATH
      # Should include turtlebot3 models directory

2. **Install robot packages**:

   .. code-block:: bash

      # TurtleBot3
      sudo apt install ros-humble-turtlebot3-gazebo

      # Crazyflie
      sudo apt install ros-humble-crazyflie  # If available

3. **Set environment variables**:

   .. code-block:: bash

      export GAZEBO_MODEL_PATH=$GAZEBO_MODEL_PATH:/opt/ros/humble/share/turtlebot3_gazebo/models

**Solution**: Ensure robot packages installed and GAZEBO_MODEL_PATH set correctly.

Robot Spawning Issues
======================

Robot Not Appearing in Gazebo
------------------------------

**Problem**: Gazebo launches but robot doesn't appear.

**Diagnostic**:

.. code-block:: python

   gz = start_gazebo(robot='turtlebot3', headless=False)
   # Gazebo window opens but environment is empty

**Common Causes**:

1. **Wrong robot name**

   .. code-block:: python

      # WRONG
      gz = start_gazebo(robot='turtlebot4')  # Not supported!

      # CORRECT - Supported robots
      gz = start_gazebo(robot='turtlebot3', model='burger')
      gz = start_gazebo(robot='crazyflie')

2. **Spawn service failed** (check logs):

   .. code-block:: bash

      # Check if spawn service is available
      ros2 service list | grep spawn

3. **Robot spawned outside view**

   .. code-block:: python

      # Check spawn position
      gz = start_gazebo(
          robot='turtlebot3',
          x_pose=0.0,  # Make sure reasonable
          y_pose=0.0,
          z_pose=0.0,  # Not underground!
          yaw=0.0
      )

**Solution**: Use supported robots, verify spawn position, check service availability.

Robot Spawns Underground
-------------------------

**Problem**: Robot immediately falls through the ground plane.

**Symptoms**:

- Robot visible for a split second then disappears
- Physics explosions or instability

**Cause**: Incorrect ``z_pose`` value (negative or too low).

**Solution**:

.. code-block:: python

   # WRONG
   gz = start_gazebo(robot='turtlebot3', z_pose=-0.5)  # Underground!

   # CORRECT
   gz = start_gazebo(
       robot='turtlebot3',
       z_pose=0.0  # For ground robots
   )

   gz = start_gazebo(
       robot='crazyflie',
       z_pose=0.5  # For aerial robots (spawn in air)
   )

Multiple Robots Not Spawning
-----------------------------

**Problem**: Trying to spawn multiple robots in one simulation.

**Note**: The current ``start_gazebo()`` wrapper supports **single-robot scenarios**. Multi-robot requires advanced ROS2 service calls.

**Workaround** (advanced):

.. code-block:: python

   import subprocess

   # Start Gazebo with first robot
   gz = start_gazebo(robot='turtlebot3', model='burger')

   # Manually spawn additional robots using ros2 service
   subprocess.run([
       'ros2', 'service', 'call',
       '/spawn_entity',
       'gazebo_msgs/srv/SpawnEntity',
       '{name: "robot2", xml: "...", initial_pose: {...}}'
   ])

**Better Solution**: See advanced multi-robot tutorials or use ROS2 launch files.

ROS Topics Issues
=================

No /odom Topic After Launch
----------------------------

**Problem**: Gazebo runs but ``/odom`` topic doesn't exist.

**Diagnostic**:

.. code-block:: bash

   ros2 topic list  # /odom missing

**Common Causes**:

1. **Robot not fully spawned yet**

   Gazebo takes 2-5 seconds to initialize topics after spawn:

   .. code-block:: python

      import time

      gz = start_gazebo(robot='turtlebot3')
      time.sleep(3)  # Wait for initialization

      # Now check topics
      !ros2 topic list

2. **Wrong robot model**

   Different models have different sensors:

   .. code-block:: python

      # TurtleBot3 Burger has /odom
      gz = start_gazebo(robot='turtlebot3', model='burger')

      # Check model-specific topics
      !ros2 topic list | grep odom

3. **ROS-Gazebo bridge not running**

   .. code-block:: bash

      # Check if bridge is running
      ros2 node list | grep bridge

**Solution**: Wait for initialization, verify robot model, check bridge process.

/cmd_vel Commands Ignored
--------------------------

**Problem**: Publishing to ``/cmd_vel`` but robot doesn't move.

**Diagnostic**:

.. code-block:: bash

   # Publish test command
   ros2 topic pub /cmd_vel geometry_msgs/msg/Twist \
     "{linear: {x: 0.2}, angular: {z: 0.0}}" --once

   # Robot should move forward

**Common Causes**:

1. **Wrong topic name**

   .. code-block:: bash

      # List available command topics
      ros2 topic list | grep cmd

      # Some robots use different names
      # TurtleBot3: /cmd_vel
      # Some platforms: /mobile_base/commands/velocity

2. **Simulation paused**

   In Gazebo GUI, check if simulation is paused (play button in bottom bar).

3. **Physics not running**

   .. code-block:: bash

      # Check Gazebo is running in real-time mode
      gz topic -l  # Should show physics topics

4. **Message format incorrect**

   .. code-block:: python

      from geometry_msgs.msg import Twist

      # WRONG: Only setting linear.x
      cmd = Twist()
      cmd.linear.x = 0.2  # Missing other fields

      # CORRECT: Full message
      cmd = Twist()
      cmd.linear.x = 0.2
      cmd.linear.y = 0.0
      cmd.linear.z = 0.0
      cmd.angular.x = 0.0
      cmd.angular.y = 0.0
      cmd.angular.z = 0.0

**Solution**: Verify topic name, ensure simulation running, check message format.

Sensor Topics Missing
---------------------

**Problem**: Robot spawned but sensor topics (``/scan``, ``/imu``) missing.

**Cause**: Robot model doesn't have those sensors equipped.

**Solution**:

.. code-block:: python

   # TurtleBot3 models have different sensors:

   # Burger: /odom, /scan, /imu
   gz = start_gazebo(robot='turtlebot3', model='burger')

   # Waffle: /odom, /scan, /imu, /camera
   gz = start_gazebo(robot='turtlebot3', model='waffle')

   # Check available sensors
   !ros2 topic list

Simulation Performance Issues
==============================

Simulation Running Very Slow
-----------------------------

**Problem**: Simulation runs much slower than real-time.

**Diagnostic**: Check real-time factor in Gazebo GUI (bottom bar shows "RTF: 0.5x" etc.)

**Solutions**:

1. **Use headless mode** (5-10x speedup):

   .. code-block:: python

      gz = start_gazebo(robot='turtlebot3', headless=True)

2. **Use simpler world**:

   .. code-block:: python

      # SLOW: Complex environment
      gz = start_gazebo(world='turtlebot3_world')

      # FAST: Minimal environment
      gz = start_gazebo(world='empty_world')

3. **Reduce physics accuracy** (advanced):

   Edit world file to increase time step, reduce iterations.

4. **Close other applications**:

   Gazebo is CPU and GPU intensive.

**Solution**: Use headless mode and simple environments for performance-critical work.

High CPU Usage
--------------

**Problem**: Gazebo consuming 100% CPU even when idle.

**Cause**: Physics engine running at maximum rate.

**Solutions**:

1. **Use headless mode**:

   .. code-block:: python

      gz = start_gazebo(headless=True)  # No rendering overhead

2. **Lower real-time factor** (if acceptable):

   This is an advanced Gazebo configuration (see Gazebo documentation).

3. **Pause simulation when not needed**:

   In Gazebo GUI, use pause button. For headless, call ROS service:

   .. code-block:: bash

      ros2 service call /pause_physics std_srvs/srv/Empty

**Solution**: Use headless mode for background simulations.

Memory Leaks
------------

**Problem**: Memory usage grows over time during long simulations.

**Symptoms**:

- RAM usage increases from 2GB to 8GB+ after hours
- System becomes unresponsive

**Cause**: Gazebo accumulates visualization data, physics states, or log data.

**Solutions**:

1. **Restart simulation periodically**:

   .. code-block:: python

      # In long-running experiments
      for trial in range(100):
          gz = start_gazebo(robot='turtlebot3', headless=True)

          # Run experiment
          run_trial(trial)

          # Clean restart every trial
          stop_gazebo(gz)
          time.sleep(2)  # Let processes fully die

2. **Use headless mode** (reduces memory usage):

   .. code-block:: python

      gz = start_gazebo(headless=True)

3. **Monitor memory**:

   .. code-block:: bash

      # Check memory usage
      htop  # or top, look for gzserver/gzclient

**Solution**: Restart simulations periodically, use headless mode.

Time and Synchronization Issues
================================

use_sim_time Not Set
---------------------

**Problem**:

.. code-block:: text

   [WARN] Parameter use_sim_time not set, defaulting to false

**Cause**: ROS nodes not configured to use Gazebo's simulation time.

**Impact**:
- Inconsistent timestamps between robot and control nodes
- tf transforms may fail
- Sensor fusion breaks

**Solution**: Set ``use_sim_time`` for **all** ROS2 nodes:

.. code-block:: python

   # In ROSNode creation (if supported)
   node._node.declare_parameter('use_sim_time', True)

   # Or via command line
   ros2 run my_package my_node --ros-args -p use_sim_time:=true

**Best Practice**: When using Gazebo, always set ``use_sim_time: true`` globally.

Timestamps in Future Warning
-----------------------------

**Problem**:

.. code-block:: text

   [WARN] Message from future! stamp=1234.5, now=1234.0

**Cause**: Some nodes using simulation time, others using wall-clock time.

**Solution**: Ensure **ALL** nodes (including your ROSNode wrappers) use ``use_sim_time: true``.

Simulation Time Not Advancing
------------------------------

**Problem**: Gazebo running but simulation time stuck at 0.

**Diagnostic**:

.. code-block:: bash

   ros2 topic echo /clock  # Should show increasing time

**Cause**: Simulation paused or physics not running.

**Solutions**:

1. **Unpause simulation**:

   In GUI: Click play button

   In code:

   .. code-block:: bash

      ros2 service call /unpause_physics std_srvs/srv/Empty

2. **Check physics engine**:

   .. code-block:: bash

      gz topic -l | grep physics  # Should show active topics

**Solution**: Ensure simulation unpaused and physics enabled.

Process Management Issues
==========================

Gazebo Won't Stop
-----------------

**Problem**: ``stop_gazebo()`` returns but processes still running.

**Diagnostic**:

.. code-block:: bash

   ps aux | grep gz  # Shows gzserver/gzclient still alive

**Solutions**:

1. **Force kill**:

   .. code-block:: bash

      pkill -9 gzserver
      pkill -9 gzclient
      pkill -9 'gz sim'
      pkill -9 ros_gz_bridge

2. **Restart notebook kernel** (in Jupyter):

   Kernel → Restart

3. **Check for zombie processes**:

   .. code-block:: bash

      ps aux | grep defunct  # Zombie processes

**Solution**: Use ``stop_gazebo()`` properly, force kill if needed.

"Address already in use" Error
-------------------------------

**Problem**: Cannot start Gazebo, port already bound.

**Error**:

.. code-block:: text

   bind: Address already in use

**Cause**: Previous Gazebo instance still holding network ports.

**Solution**:

.. code-block:: bash

   # Find processes using Gazebo ports
   lsof -i :11345  # Gazebo master port

   # Kill them
   pkill -9 gzserver
   pkill -9 gzclient

   # Wait and retry
   sleep 2

Multiple Gazebo Instances
--------------------------

**Problem**: Accidentally started multiple Gazebo instances.

**Symptoms**:

- Multiple Gazebo windows
- Extreme CPU usage
- Topic confusion

**Solution**:

.. code-block:: bash

   # Kill ALL Gazebo processes
   pkill -9 gzserver
   pkill -9 gzclient
   pkill -9 'gz sim'

   # Verify
   ps aux | grep gz

**Prevention**: Always call ``stop_gazebo()`` before starting new simulation.

Headless Mode Issues
=====================

Headless Mode Still Shows Window
---------------------------------

**Problem**: Set ``headless=True`` but Gazebo GUI still appears.

**Cause**: Gazebo client (gzclient) incorrectly launched.

**Diagnostic**:

.. code-block:: bash

   ps aux | grep gzclient  # Should NOT exist in headless mode

**Solution**: Verify ``headless=True`` is set, restart if needed.

Headless Mode Slower Than Expected
-----------------------------------

**Problem**: ``headless=True`` but simulation still slow.

**Cause**: World complexity or physics iterations, not rendering.

**Solutions**:

1. **Use simpler world**:

   .. code-block:: python

      # Minimal world
      gz = start_gazebo(
          robot='turtlebot3',
          world='empty_world',  # Fastest
          headless=True
      )

2. **Reduce physics accuracy** (advanced configuration).

**Solution**: Headless mode removes rendering overhead, but physics still runs at full fidelity.

World and Environment Issues
=============================

World Not Loading
-----------------

**Problem**: Gazebo starts but world is black/empty.

**Cause**: World file not found or corrupted.

**Solutions**:

1. **Use supported worlds**:

   .. code-block:: python

      # Known working worlds
      supported_worlds = [
          'empty_world',
          'turtlebot3_world',
          'turtlebot3_house',
      ]

      gz = start_gazebo(robot='turtlebot3', world='empty_world')

2. **Check world file exists**:

   .. code-block:: bash

      find /opt/ros/humble -name "*.world" | grep turtlebot3

**Solution**: Use known-good worlds, verify world files installed.

Robot-World Collision Issues
-----------------------------

**Problem**: Robot phases through obstacles or gets stuck in walls.

**Cause**: Physics parameters or collision meshes misconfigured.

**Solutions**:

1. **Spawn robot away from obstacles**:

   .. code-block:: python

      gz = start_gazebo(
          robot='turtlebot3',
          x_pose=0.0,  # Open space
          y_pose=0.0,
          z_pose=0.0
      )

2. **Check collision models** (advanced):

   Inspect robot's collision meshes in model files.

**Solution**: Ensure robot spawns in clear space, verify collision geometry.

Debugging Strategies
====================

Enable Verbose Logging
----------------------

.. code-block:: bash

   # Set Gazebo verbosity
   export GAZEBO_VERBOSE=1

   # Set ROS2 verbosity
   export RCUTILS_CONSOLE_OUTPUT_FORMAT="[{severity}] [{name}]: {message}"

Check Gazebo Topics
-------------------

.. code-block:: bash

   # List all Gazebo topics
   gz topic -l

   # Echo specific topic
   gz topic -e -t /gazebo/default/pose/info

Check ROS2-Gazebo Bridge
------------------------

.. code-block:: bash

   # Verify bridge is running
   ros2 node list | grep bridge

   # Check bridge parameters
   ros2 param list /ros_gz_bridge

Test Without dynamicalnodes Wrapper
---------------------------

.. code-block:: bash

   # Launch Gazebo manually
   gazebo --verbose

   # If this fails, issue is with Gazebo installation, not dynamicalnodes

Monitor System Resources
-------------------------

.. code-block:: bash

   # CPU and memory
   htop

   # GPU (if using GUI)
   nvidia-smi  # For NVIDIA GPUs

   # Disk I/O
   iotop

Common Error Messages Reference
================================

Quick lookup for Gazebo errors:

+------------------------------------------------+----------------------------------+
| Error Message                                  | Solution                         |
+================================================+==================================+
| ``libGL error: failed to load driver``         | Use ``headless=True``            |
+------------------------------------------------+----------------------------------+
| ``Model not found``                            | Install robot packages,          |
|                                                | set GAZEBO_MODEL_PATH            |
+------------------------------------------------+----------------------------------+
| ``Address already in use``                     | Kill existing Gazebo: pkill -9   |
+------------------------------------------------+----------------------------------+
| ``use_sim_time not set``                       | Set ``use_sim_time: true``       |
+------------------------------------------------+----------------------------------+
| ``No /odom topic``                             | Wait 3s for spawn, check model   |
+------------------------------------------------+----------------------------------+
| ``Robot won't move``                           | Check /cmd_vel topic, unpause    |
+------------------------------------------------+----------------------------------+
| ``Simulation very slow``                       | Use headless, empty_world        |
+------------------------------------------------+----------------------------------+
| ``High memory usage``                          | Restart periodically, headless   |
+------------------------------------------------+----------------------------------+
| ``Timestamps from future``                     | Sync use_sim_time across nodes   |
+------------------------------------------------+----------------------------------+
| ``Gazebo won't stop``                          | pkill -9 gzserver gzclient       |
+------------------------------------------------+----------------------------------+

Getting Help
============

If you encounter issues not covered here:

1. **Check documentation**:
   - dynamicalnodes docs: https://dynamicalnodes.readthedocs.io
   - Gazebo docs: https://gazebosim.org/docs
   - ROS2-Gazebo docs: https://github.com/ros-simulation/gazebo_ros_pkgs

2. **Search existing issues**:
   - Gazebo Answers: https://answers.gazebosim.org
   - ROS Answers: https://answers.ros.org

3. **Ask for help**:
   - Create issue with:
     - Gazebo version (``gazebo --version``)
     - ROS2 version (``ros2 --version``)
     - Error logs
     - Minimal reproducible example

4. **Common resources**:
   - Gazebo tutorials: https://gazebosim.org/tutorials
   - ROS2-Gazebo integration: https://docs.ros.org/en/humble/Tutorials/Advanced/Simulators/Gazebo.html

Summary
=======

**Most Common Issues**:

1. ✗ Missing ROS2 Gazebo packages
2. ✗ Graphics errors (use ``headless=True``)
3. ✗ Robot not spawning (wrong model name)
4. ✗ Topics not appearing (wait for initialization)
5. ✗ Simulation too slow (use headless + empty_world)
6. ✗ Gazebo won't stop (pkill -9)
7. ✗ use_sim_time not synchronized
8. ✗ Multiple Gazebo instances running

**Debugging Workflow**:

1. Check Gazebo is installed: ``gazebo --version``
2. Verify ROS2 packages: ``ros2 pkg list | grep gazebo``
3. Use headless mode for testing: ``headless=True``
4. Check topic list: ``ros2 topic list``
5. Monitor processes: ``ps aux | grep gz``
6. Check logs: ``export GAZEBO_VERBOSE=1``
7. Test manually: ``gazebo --verbose``

**Best Practices**:

✓ Always use ``stop_gazebo()`` for cleanup
✓ Use ``headless=True`` for performance
✓ Wait 2-3s after spawn for topics to initialize
✓ Set ``use_sim_time: true`` when using Gazebo
✓ Use ``empty_world`` for fastest simulation
✓ Kill zombie processes: ``pkill -9 gzserver``
✓ Restart simulations periodically for long runs
✓ Test with minimal setup first (empty_world, single robot)

:doc:`← ROS to Gazebo <index>`
