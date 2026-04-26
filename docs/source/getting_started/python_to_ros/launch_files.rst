:doc:`← Python to ROS <index>`

======================
ROS2 Launch Files with dynamicalnodes
======================

In the tutorials so far, we've been manually creating and starting nodes one by one in Jupyter notebooks. This is great for learning, but professional ROS development uses **launch files** to start entire systems with a single command.

This guide shows how to create Python launch files for ``dynamicalnodes`` ROS systems.

Why Launch Files?
=================

**Without Launch Files** (manual):

.. code-block:: python

   # Start each node individually
   rclpy.init()
   waypoint_node.create_node()
   controller_node.create_node()
   simulator_node.create_node()
   kf_node.create_node()
   
   waypoint_node.start()
   controller_node.start()
   simulator_node.start()
   kf_node.start()
   
   # Must manage lifecycle manually

**With Launch Files** (automated):

.. code-block:: bash

   ros2 launch dynamicalnodes_demos turtlebot_navigation.launch.py

**Benefits**:

✓ Start entire system with one command
✓ Configure parameters from one place
✓ Handle node dependencies and startup order
✓ Easily switch between simulation/hardware
✓ Share reproducible setups
✓ Professional standard for ROS

ROS2 Launch File Basics
========================

ROS2 uses **Python launch files** (not XML like ROS1):

.. code-block:: python

   from launch import LaunchDescription
   from launch_ros.actions import Node
   
   def generate_launch_description():
       return LaunchDescription([
           Node(
               package='package_name',
               executable='node_executable',
               name='node_name',
               parameters=[{'param': value}]
           ),
       ])

Launch File Structure for dynamicalnodes
================================

Since ``dynamicalnodes`` nodes are created programmatically (not from executables), we use a different approach:

**Option 1: Create a Standalone Script**
----------------------------------------

Create a Python script that runs nodes:

.. code-block:: python

   # scripts/turtlebot_system.py
   import rclpy
   from dynamicalnodes_demos.turtlebot_nodes import (
       create_waypoint_node,
       create_controller_node,
       create_simulator_node,
       create_kf_node
   )
   
   def main():
       rclpy.init()
       
       # Create nodes
       waypoint_node = create_waypoint_node()
       controller_node = create_controller_node()
       simulator_node = create_simulator_node()
       kf_node = create_kf_node()
       
       # Create and start
       waypoint_node.create_node()
       controller_node.create_node()
       simulator_node.create_node()
       kf_node.create_node()
       
       waypoint_node.start()
       controller_node.start()
       simulator_node.start()
       kf_node.start()
       
       # Keep running
       try:
           rclpy.spin(waypoint_node._node)
       except KeyboardInterrupt:
           pass
       
       # Cleanup
       waypoint_node.stop()
       controller_node.stop()
       simulator_node.stop()
       kf_node.stop()
       rclpy.shutdown()
   
   if __name__ == '__main__':
       main()

Then launch with:

.. code-block:: bash

   python3 scripts/turtlebot_system.py

**Option 2: Use Launch File to Run Script**
-------------------------------------------

Create a launch file that runs the script:

.. code-block:: python

   # launch/turtlebot_navigation.launch.py
   from launch import LaunchDescription
   from launch.actions import ExecuteProcess
   import os
   
   def generate_launch_description():
       script_path = os.path.join(
           os.path.dirname(__file__),
           '..',
           'scripts',
           'turtlebot_system.py'
       )
       
       return LaunchDescription([
           ExecuteProcess(
               cmd=['python3', script_path],
               output='screen'
           )
       ])

Then launch with:

.. code-block:: bash

   ros2 launch dynamicalnodes_demos turtlebot_navigation.launch.py

**Option 3: Multi-Process Launch (Recommended)**
-------------------------------------------------

Launch each ROSNode as a separate process for better isolation:

.. code-block:: python

   # launch/turtlebot_multiprocess.launch.py
   from launch import LaunchDescription
   from launch.actions import ExecuteProcess
   import os
   
   def generate_launch_description():
       scripts_dir = os.path.join(os.path.dirname(__file__), '..', 'scripts')
       
       return LaunchDescription([
           ExecuteProcess(
               cmd=['python3', os.path.join(scripts_dir, 'waypoint_node.py')],
               output='screen',
               prefix='xterm -e'  # Open in separate terminal
           ),
           ExecuteProcess(
               cmd=['python3', os.path.join(scripts_dir, 'controller_node.py')],
               output='screen',
               prefix='xterm -e'
           ),
           ExecuteProcess(
               cmd=['python3', os.path.join(scripts_dir, 'simulator_node.py')],
               output='screen',
               prefix='xterm -e'
           ),
           ExecuteProcess(
               cmd=['python3', os.path.join(scripts_dir, 'kf_node.py')],
               output='screen',
               prefix='xterm -e'
           ),
       ])

Each node runs in its own terminal window for easy debugging!

Example: TurtleBot Launch System
=================================

Let's create a complete launch system for TurtleBot navigation.

**Directory Structure**::

   dynamicalnodes_demos/
   ├── launch/
   │   ├── turtlebot_software.launch.py
   │   ├── turtlebot_gazebo.launch.py
   │   └── crazyflie_fusion.launch.py
   ├── scripts/
   │   ├── turtlebot_waypoint_node.py
   │   ├── turtlebot_controller_node.py
   │   ├── turtlebot_simulator_node.py
   │   └── turtlebot_kf_node.py
   └── config/
       └── turtlebot_params.yaml

**1. Create Node Scripts**

Each node in its own file:

.. code-block:: python

   # scripts/turtlebot_waypoint_node.py
   import rclpy
   from dynamicalnodes.ros.ros_node import ROSNode
   from geometry_msgs.msg import PoseStamped
   import numpy as np
   
   def create_waypoint_node():
       # ... (node creation code)
       pass
   
   def main():
       rclpy.init()
       node = create_waypoint_node()
       node.create_node()
       node.start()
       
       try:
           rclpy.spin(node._node)
       except KeyboardInterrupt:
           pass
       
       node.stop()
       rclpy.shutdown()
   
   if __name__ == '__main__':
       main()

**2. Create Launch File**

.. code-block:: python

   # launch/turtlebot_software.launch.py
   from launch import LaunchDescription
   from launch.actions import ExecuteProcess, DeclareLaunchArgument
   from launch.substitutions import LaunchConfiguration
   import os
   from ament_index_python.packages import get_package_share_directory
   
   def generate_launch_description():
       # Declare arguments
       use_sim_time = LaunchConfiguration('use_sim_time', default='false')
       
       # Get package directory
       pkg_dir = get_package_share_directory('dynamicalnodes_demos')
       scripts_dir = os.path.join(pkg_dir, 'scripts')
       
       return LaunchDescription([
           # Arguments
           DeclareLaunchArgument(
               'use_sim_time',
               default_value='false',
               description='Use simulation time'
           ),
           
           # Nodes
           ExecuteProcess(
               cmd=['python3', os.path.join(scripts_dir, 'turtlebot_waypoint_node.py')],
               output='screen'
           ),
           ExecuteProcess(
               cmd=['python3', os.path.join(scripts_dir, 'turtlebot_controller_node.py')],
               output='screen'
           ),
           ExecuteProcess(
               cmd=['python3', os.path.join(scripts_dir, 'turtlebot_simulator_node.py')],
               output='screen'
           ),
           ExecuteProcess(
               cmd=['python3', os.path.join(scripts_dir, 'turtlebot_kf_node.py')],
               output='screen'
           ),
       ])

**3. Launch**

.. code-block:: bash

   ros2 launch dynamicalnodes_demos turtlebot_software.launch.py

Launching with Gazebo
======================

For Gazebo integration, modify the launch file:

.. code-block:: python

   # launch/turtlebot_gazebo.launch.py
   from launch import LaunchDescription
   from launch.actions import ExecuteProcess, IncludeLaunchDescription
   from launch.launch_description_sources import PythonLaunchDescriptionSource
   import os
   
   def generate_launch_description():
       # Start Gazebo
       gazebo_launch = IncludeLaunchDescription(
           PythonLaunchDescriptionSource([
               os.path.join(
                   get_package_share_directory('gazebo_ros'),
                   'launch',
                   'gazebo.launch.py'
               )
           ])
       )
       
       # Spawn TurtleBot model
       spawn_robot = ExecuteProcess(
           cmd=['ros2', 'run', 'gazebo_ros', 'spawn_entity.py',
                '-entity', 'turtlebot3',
                '-topic', 'robot_description'],
           output='screen'
       )
       
       # Start dynamicalnodes nodes (NO simulator this time!)
       pkg_dir = get_package_share_directory('dynamicalnodes_demos')
       scripts_dir = os.path.join(pkg_dir, 'scripts')
       
       return LaunchDescription([
           gazebo_launch,
           spawn_robot,
           ExecuteProcess(
               cmd=['python3', os.path.join(scripts_dir, 'turtlebot_waypoint_node.py')],
               output='screen'
           ),
           ExecuteProcess(
               cmd=['python3', os.path.join(scripts_dir, 'turtlebot_controller_node.py')],
               output='screen'
           ),
           # NOTE: NO simulator_node - Gazebo provides /odom!
           ExecuteProcess(
               cmd=['python3', os.path.join(scripts_dir, 'turtlebot_kf_node.py')],
               output='screen'
           ),
       ])

Parameter Files
===============

Use YAML files for configuration:

.. code-block:: yaml

   # config/turtlebot_params.yaml
   waypoint_generator:
     ros__parameters:
       rate_hz: 10.0
       waypoints:
         - [2.0, 0.0, 0.0]
         - [2.0, 2.0, 1.57]
         - [0.0, 2.0, 3.14]
         - [0.0, 0.0, -1.57]
       switch_time: 15.0
   
   velocity_controller:
     ros__parameters:
       Kp: 0.5
       Komega: 1.5
       rate_hz: 50.0
   
   kalman_filter:
     ros__parameters:
       dt: 0.1
       rate_hz: 10.0
       Q_diag: [0.01, 0.01, 0.02, 0.1, 0.1]
       R_diag: [0.05, 0.05, 0.1]

Load in launch file:

.. code-block:: python

   from launch_ros.actions import Node
   
   Node(
       package='dynamicalnodes_demos',
       executable='turtlebot_kf_node.py',
       parameters=[os.path.join(pkg_dir, 'config', 'turtlebot_params.yaml')]
   )

Advanced Launch Features
=========================

Conditional Launching
---------------------

Launch different nodes based on arguments:

.. code-block:: python

   from launch.conditions import IfCondition, UnlessCondition
   
   use_gazebo = LaunchConfiguration('gazebo')
   
   # Launch simulator only if NOT using Gazebo
   ExecuteProcess(
       cmd=['python3', 'simulator_node.py'],
       condition=UnlessCondition(use_gazebo)
   )
   
   # Launch Gazebo only if using Gazebo
   IncludeLaunchDescription(...,
       condition=IfCondition(use_gazebo)
   )

Node Dependencies
-----------------

Ensure nodes start in correct order:

.. code-block:: python

   from launch.actions import RegisterEventHandler
   from launch.event_handlers import OnProcessStart
   
   # Start controller only after simulator is ready
   RegisterEventHandler(
       OnProcessStart(
           target_action=simulator_node,
           on_start=[controller_node]
       )
   )

Namespace Management
--------------------

Run multiple robots with namespaces:

.. code-block:: python

   robot1 = Node(
       package='dynamicalnodes_demos',
       executable='turtlebot_system',
       namespace='robot1'
   )
   
   robot2 = Node(
       package='dynamicalnodes_demos',
       executable='turtlebot_system',
       namespace='robot2'
   )

Topics become: ``/robot1/odom``, ``/robot2/odom``, etc.

Testing Launch Files
=====================

Verify your launch file works:

.. code-block:: bash

   # Check syntax
   ros2 launch --show-args dynamicalnodes_demos turtlebot_software.launch.py
   
   # List all nodes that will be launched
   ros2 launch --show-nodes dynamicalnodes_demos turtlebot_software.launch.py
   
   # Actually launch
   ros2 launch dynamicalnodes_demos turtlebot_software.launch.py

Debugging launch issues:

.. code-block:: bash

   # Verbose output
   ros2 launch dynamicalnodes_demos turtlebot_software.launch.py --debug
   
   # Check if nodes are running
   ros2 node list
   
   # Check topics
   ros2 topic list
   
   # Monitor logs
   ros2 launch dynamicalnodes_demos turtlebot_software.launch.py --screen

Best Practices
==============

1. **One launch file per use case**:
   - ``turtlebot_software.launch.py`` - Software simulation
   - ``turtlebot_gazebo.launch.py`` - Gazebo integration
   - ``turtlebot_hardware.launch.py`` - Real hardware

2. **Parameterize everything**:
   - Use launch arguments for flexibility
   - Store parameters in YAML files
   - Allow runtime configuration

3. **Descriptive naming**:
   - Launch files: ``<robot>_<use_case>.launch.py``
   - Nodes: ``<robot>_<component>_node.py``
   - Configs: ``<robot>_params.yaml``

4. **Document your launch files**:
   - Add docstrings
   - Explain arguments
   - Provide usage examples

5. **Test incrementally**:
   - Start with one node
   - Add nodes one at a time
   - Verify with ``rqt_graph``

Summary
=======

Launch files are essential for professional ROS development:

✓ **Automation**: Start entire systems with one command
✓ **Configuration**: Centralize parameters
✓ **Reproducibility**: Share exact setups
✓ **Flexibility**: Switch between simulation/hardware
✓ **Debugging**: Better logging and process management

For ``dynamicalnodes`` systems:

1. Create standalone node scripts
2. Create launch file to run scripts
3. Use parameter files for configuration
4. Test with ``ros2 launch``
5. Verify with ``rqt_graph``

**Next**: Apply this to your TurtleBot and Crazyflie systems for professional deployment!

:doc:`← Python to ROS <index>`
