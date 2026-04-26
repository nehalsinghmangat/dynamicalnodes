:doc:`← ROS to Gazebo <index>`

================================
Deploying to Real Hardware
================================

The final step: taking your ``dynamicalnodes`` control system from Gazebo simulation to **real robots**. This guide covers the complete workflow for deploying to TurtleBot3 and Crazyflie hardware.

.. contents:: Quick Navigation
   :local:
   :depth: 2

The Deployment Pipeline
=======================

Your dynamicalnodes system has progressed through:

1. **Theory** → Mathematical models and algorithms
2. **Python** → DynamicalSystem implementations  
3. **ROS** → ROSNode wrappers and software simulation
4. **Gazebo** → Physics-based simulation
5. **Hardware** → Real robot deployment ← *You are here*

**The Beautiful Part**: Your control/estimation code **doesn't change** between simulation and hardware!

What Changes: Software → Gazebo → Hardware
===========================================

+-------------------+----------------------+----------------------+---------------------+
| Component         | Software Sim         | Gazebo Sim           | Real Hardware       |
+===================+======================+======================+=====================+
| **Plant**         | Python function      | Gazebo physics       | Actual robot        |
+-------------------+----------------------+----------------------+---------------------+
| **Sensors**       | Python function      | Gazebo sensors       | Real sensors        |
+-------------------+----------------------+----------------------+---------------------+
| **Controller**    | **ROSNode**          | **ROSNode**          | **ROSNode**         |
+-------------------+----------------------+----------------------+---------------------+
| **Observer**      | **ROSNode**          | **ROSNode**          | **ROSNode**         |
+-------------------+----------------------+----------------------+---------------------+
| **Topics**        | /cmd_vel, /odom      | /cmd_vel, /odom      | /cmd_vel, /odom     |
+-------------------+----------------------+----------------------+---------------------+

**Key Insight**: Only the *source* of sensor data and *target* of commands changes. Your control logic stays identical!

Prerequisites
=============

Hardware Requirements
---------------------

**For TurtleBot3**:

- TurtleBot3 Burger or Waffle  
- Raspberry Pi with Ubuntu + ROS2
- WiFi network (same as development machine)
- Battery charged
- Emergency stop button (recommended)

**For Crazyflie**:

- Crazyflie 2.1 quadrotor
- Crazyradio PA USB dongle
- Motion capture system (OptiTrack, Vicon) or Lighthouse positioning
- Battery charged
- Safety net/cage for indoor flight

Software Requirements
---------------------

**On Development Machine**:

.. code-block:: bash

   # Your dynamicalnodes system (already have)
   # ROS2 Humble
   # Network access to robot

**On Robot (TurtleBot3)**:

.. code-block:: bash

   # Ubuntu 22.04 + ROS2 Humble
   # turtlebot3_bringup package
   # Network access to development machine

**On Robot (Crazyflie)**:

.. code-block:: bash

   # Crazyswarm2 or crazyflie_ros packages
   # Configured for your positioning system

Safety First!
=============

**Before ANY hardware test**:

1. ✓ **Test in simulation first** - Gazebo should work perfectly
2. ✓ **Start with low gains** - Conservative controller parameters
3. ✓ **Have emergency stop** - Physical button or keyboard shortcut
4. ✓ **Clear workspace** - Remove obstacles, fragile items
5. ✓ **Short test durations** - Start with 5-10 second tests
6. ✓ **Human oversight** - Never leave robot unattended
7. ✓ **Battery check** - Ensure sufficient charge

**Emergency Stop Procedures**:

- **TurtleBot3**: Press emergency button or ``Ctrl+C`` in terminal
- **Crazyflie**: Release thrust command or press keyboard shortcut
- **Both**: Unplug battery if necessary

TurtleBot3 Deployment
=====================

Step 1: Setup TurtleBot3 Hardware
----------------------------------

**On TurtleBot3 Raspberry Pi**:

.. code-block:: bash

   # SSH into TurtleBot
   ssh ubuntu@{TURTLEBOT_IP}
   
   # Source ROS2
   source /opt/ros/humble/setup.bash
   source ~/turtlebot3_ws/install/setup.bash
   
   # Set robot model
   export TURTLEBOT3_MODEL=burger
   
   # Launch robot bringup (provides /odom, accepts /cmd_vel)
   ros2 launch turtlebot3_bringup robot.launch.py

This starts:

- **Motor controllers** (accept /cmd_vel)
- **Wheel encoders** (publish /odom)
- **LiDAR** (publish /scan)
- **IMU** (publish /imu)

**Verify topics on development machine**:

.. code-block:: bash

   # Check robot is publishing
   ros2 topic list  # Should see /odom, /scan, /cmd_vel
   ros2 topic hz /odom  # Should be ~30 Hz
   ros2 topic echo /cmd_vel  # Should be empty (no commands yet)

Step 2: Modify Launch File for Hardware
----------------------------------------

**Before (Gazebo)**:

.. code-block:: python

   # launch/turtlebot_gazebo.launch.py
   from launch import LaunchDescription
   from launch.actions import ExecuteProcess, IncludeLaunchDescription
   
   def generate_launch_description():
       return LaunchDescription([
           # Start Gazebo (provides /odom, accepts /cmd_vel)
           IncludeLaunchDescription(...),
           
           # Start dynamicalnodes nodes
           ExecuteProcess(cmd=['python3', 'waypoint_node.py']),
           ExecuteProcess(cmd=['python3', 'controller_node.py']),
           ExecuteProcess(cmd=['python3', 'kf_node.py']),
       ])

**After (Hardware)**:

.. code-block:: python

   # launch/turtlebot_hardware.launch.py
   from launch import LaunchDescription
   from launch.actions import ExecuteProcess
   
   def generate_launch_description():
       return LaunchDescription([
           # NO Gazebo launch!
           # Robot bringup already running on TurtleBot
           
           # Start dynamicalnodes nodes (IDENTICAL to Gazebo!)
           ExecuteProcess(cmd=['python3', 'waypoint_node.py']),
           ExecuteProcess(cmd=['python3', 'controller_node.py']),
           ExecuteProcess(cmd=['python3', 'kf_node.py']),
       ])

**That's it!** The only change is removing Gazebo launch.

Step 3: Run Hardware Test
--------------------------

**On development machine**:

.. code-block:: bash

   # Ensure network connectivity
   export ROS_DOMAIN_ID=0  # Match TurtleBot
   
   # Launch dynamicalnodes nodes
   ros2 launch my_package turtlebot_hardware.launch.py

**Expected behavior**:

1. Waypoint node publishes reference trajectory
2. Controller node subscribes to /odom and /reference
3. Controller publishes /cmd_vel
4. TurtleBot moves!
5. Kalman filter estimates state from /odom

**Monitor with rqt_graph**:

.. code-block:: bash

   rqt_graph

You should see:

::

   [Waypoint] → /reference → [Controller]
                               ↓
                            /cmd_vel → [TurtleBot Hardware]
                               ↑
   [KF] ← /odom ←────────────┘

Step 4: Tuning for Hardware
----------------------------

Hardware differs from simulation! Tune parameters:

**Controller Gains**:

.. code-block:: python

   # Simulation (Gazebo)
   Kp = 1.0
   Kd = 0.5
   
   # Hardware (start conservative!)
   Kp = 0.3  # Lower gains for safety
   Kd = 0.1

**Kalman Filter Noise**:

.. code-block:: python

   # Simulation (perfect model)
   Q = np.diag([0.01, 0.01, 0.02])
   R = np.diag([0.05, 0.05, 0.1])
   
   # Hardware (real sensors, unmodeled dynamics)
   Q = np.diag([0.1, 0.1, 0.2])   # Higher process noise
   R = np.diag([0.02, 0.02, 0.05]) # Lower measurement noise (encoders are good!)

**Rate Limits**:

.. code-block:: python

   # Hardware may not achieve 100 Hz
   # Start with 10-20 Hz
   rate_hz = 10.0

Iterate: Test → Observe → Tune → Repeat

Crazyflie Deployment
====================

Step 1: Setup Crazyflie System
-------------------------------

**Install Crazyswarm2**:

.. code-block:: bash

   # Clone repository
   cd ~/ros2_ws/src
   git clone https://github.com/IMRCLab/crazyswarm2.git
   
   # Build
   cd ~/ros2_ws
   colcon build --packages-select crazyswarm2
   source install/setup.bash

**Configure Crazyradio**:

.. code-block:: bash

   # Plug in Crazyradio PA dongle
   # Ensure permissions
   sudo groupadd plugdev
   sudo usermod -a -G plugdev $USER

**Configure Motion Capture** (if using):

Edit ``~/ros2_ws/src/crazyswarm2/config/crazyflies.yaml``:

.. code-block:: yaml

   robots:
     - id: 1
       channel: 100
       initialPosition: [0.0, 0.0, 0.0]
       type: cf21

Step 2: Test Crazyflie Communication
-------------------------------------

.. code-block:: bash

   # Launch Crazyswarm2 server
   ros2 launch crazyswarm2 launch.py
   
   # Check topics
   ros2 topic list  # Should see /cf1/pose, /cf1/cmd_vel, etc.
   
   # Test manual flight
   ros2 run crazyswarm2 teleop_twist_keyboard

Step 3: Modify dynamicalnodes Nodes for Hardware
----------------------------------------

**Key Differences**:

- Crazyflie uses ``/cf1/pose`` instead of ``/odom``
- Position control uses ``/cf1/cmd_position`` instead of ``/cmd_vel``
- Must send takeoff/land commands

**Updated Controller Node**:

.. code-block:: python

   # Before (simulation)
   controller_node = ROSNode(
       node_name='position_controller',
       subscribes_to=[
           ('/estimate', Odometry, 'estimate'),
           ('/setpoint', PoseStamped, 'setpoint')
       ],
       publishes_to=[
           ('cmd_vel', Twist, '/cmd_vel')
       ],
       rate_hz=50.0
   )
   
   # After (hardware)
   controller_node = ROSNode(
       node_name='position_controller',
       subscribes_to=[
           ('/cf1/pose', PoseStamped, 'estimate'),  # Different topic!
           ('/setpoint', PoseStamped, 'setpoint')
       ],
       publishes_to=[
           ('cmd_position', PoseStamped, '/cf1/cmd_position')  # Different message!
       ],
       rate_hz=50.0
   )

**Takeoff/Landing Sequence**:

.. code-block:: python

   from crazyflie_interfaces.srv import Takeoff, Land
   
   def takeoff_crazyflie(node, height=0.5, duration=2.0):
       client = node.create_client(Takeoff, '/cf1/takeoff')
       request = Takeoff.Request()
       request.height = height
       request.duration = rclpy.duration.Duration(seconds=duration).to_msg()
       client.call_async(request)
   
   def land_crazyflie(node, duration=2.0):
       client = node.create_client(Land, '/cf1/land')
       request = Land.Request()
       request.duration = rclpy.duration.Duration(seconds=duration).to_msg()
       client.call_async(request)

Step 4: Hardware Safety for Quadrotors
---------------------------------------

**CRITICAL: Crazyflie-specific safety!**

1. **Start on ground** - Don't launch while holding
2. **Test in net/cage first** - Contain crashes
3. **Low altitude** - Start at 0.3-0.5m height
4. **Short flights** - 10-20 second tests initially
5. **Battery monitor** - Land at 20% remaining
6. **Failsafe** - Know how to trigger emergency land

**Emergency Land**:

.. code-block:: bash

   # Keyboard shortcut
   ros2 service call /cf1/emergency std_srvs/srv/Empty
   
   # Or kill all nodes
   pkill -9 python3

Step 5: Run Hardware Flight Test
---------------------------------

.. code-block:: bash

   # Terminal 1: Crazyswarm2
   ros2 launch crazyswarm2 launch.py
   
   # Terminal 2: dynamicalnodes nodes
   ros2 launch my_package crazyflie_hardware.launch.py
   
   # Terminal 3: Takeoff
   ros2 service call /cf1/takeoff crazyflie_interfaces/srv/Takeoff \
       "{height: 0.5, duration: {sec: 2, nanosec: 0}}"
   
   # ... observe flight ...
   
   # Terminal 3: Land
   ros2 service call /cf1/land crazyflie_interfaces/srv/Land \
       "{duration: {sec: 2, nanosec: 0}}"

Network Configuration
=====================

Multi-Machine ROS2 Setup
-------------------------

**On both development machine and robot**:

.. code-block:: bash

   # Set same ROS_DOMAIN_ID
   export ROS_DOMAIN_ID=42
   
   # Set ROS_LOCALHOST_ONLY to 0
   export ROS_LOCALHOST_ONLY=0
   
   # Add to ~/.bashrc for persistence
   echo "export ROS_DOMAIN_ID=42" >> ~/.bashrc
   echo "export ROS_LOCALHOST_ONLY=0" >> ~/.bashrc

**Verify connectivity**:

.. code-block:: bash

   # On development machine
   ros2 topic pub /test std_msgs/msg/String "{data: 'hello'}"
   
   # On robot
   ros2 topic echo /test  # Should see messages

WiFi Optimization
-----------------

For reliable communication:

.. code-block:: bash

   # Check latency
   ping {ROBOT_IP}  # Should be < 5ms on local network
   
   # Use 5GHz WiFi if available (less interference)
   # Avoid obstacles between development machine and robot
   # Use static IP addresses (DHCP can cause delays)

Debugging Hardware Issues
==========================

"Robot doesn't respond to commands"
------------------------------------

**Check**:

1. Is robot bringup running?

   .. code-block:: bash

      # On robot
      ros2 node list  # Should see turtlebot3 nodes

2. Are commands being published?

   .. code-block:: bash

      ros2 topic hz /cmd_vel  # Should match controller rate

3. Are commands reaching robot?

   .. code-block:: bash

      # On robot
      ros2 topic echo /cmd_vel

4. Network delay?

   .. code-block:: bash

      ros2 topic delay /cmd_vel  # Should be < 50ms

"Odometry is noisy/wrong"
--------------------------

**Wheel encoders (TurtleBot3)**:

- Check for wheel slippage
- Ensure robot on flat surface
- Calibrate odometry if necessary

**Motion capture (Crazyflie)**:

- Verify marker visibility
- Check coordinate frame transformations
- Increase marker count for better accuracy

"Robot behaves erratically"
----------------------------

**Common causes**:

1. **Gains too high** - Reduce Kp, Kd
2. **Network latency** - Check ping times
3. **Dropped messages** - Monitor with ``ros2 topic hz``
4. **Battery low** - Charge/replace battery
5. **Sensor noise** - Increase R in Kalman filter

Performance Comparison: Sim vs Hardware
========================================

Expected Differences
--------------------

+----------------------+-------------------+-------------------+
| Metric               | Gazebo            | Hardware          |
+======================+===================+===================+
| **Tracking Error**   | < 5 cm            | 5-15 cm           |
+----------------------+-------------------+-------------------+
| **Settling Time**    | 2-3 sec           | 3-5 sec           |
+----------------------+-------------------+-------------------+
| **Overshoot**        | < 10%             | 10-20%            |
+----------------------+-------------------+-------------------+
| **Steady-State**     | Near zero         | Varies with drift |
+----------------------+-------------------+-------------------+

**Why hardware performs worse**:

- Unmodeled dynamics (friction, backlash, air resistance)
- Sensor noise and calibration errors
- Actuator limitations and delays
- External disturbances

**This is normal!** Real-world robotics is harder than simulation.

Data Collection
---------------

Record data for comparison:

.. code-block:: bash

   # Record topics
   ros2 bag record /odom /cmd_vel /estimate /reference
   
   # Replay later
   ros2 bag play my_experiment.bag
   
   # Plot in Python
   # ... (use rosbag2 Python API)

Best Practices for Hardware Deployment
=======================================

1. **Incremental Testing**

   - Test each component independently
   - Start with open-loop control
   - Add feedback gradually
   - Increase complexity slowly

2. **Conservative Initial Parameters**

   - Low controller gains
   - High filter noise covariances
   - Slow reference trajectories
   - Short test durations

3. **Comprehensive Monitoring**

   - Use ``rqt_graph`` to verify connections
   - Monitor topics with ``ros2 topic echo``
   - Log data with ``ros2 bag record``
   - Watch for error messages in terminals

4. **Iterative Tuning**

   - Change one parameter at a time
   - Record baseline performance
   - Compare before/after results
   - Document successful configurations

5. **Safety Protocols**

   - Never skip simulation testing
   - Always have emergency stop ready
   - Test in safe environment first
   - Supervise all hardware runs

Common Workflow: Sim to Hardware
=================================

**Week 1: Software Simulation**

.. code-block:: python

   # Implement in pure Python
   plant = DynamicalSystem(f=dynamics, h=sensors, state_name='x')
   controller = DynamicalSystem(f=control_law, state_name='u')
   # Test, tune, verify

**Week 2: ROS Integration**

.. code-block:: python

   # Wrap in ROSNodes
   plant_node = ROSNode(callback=plant_callback, ...)
   controller_node = ROSNode(callback=controller_callback, ...)
   # Test communication, verify topics

**Week 3: Gazebo Simulation**

.. code-block:: bash

   # Replace plant with Gazebo
   ros2 launch my_package gazebo.launch.py
   # Tune for realistic physics, test edge cases

**Week 4: Hardware Deployment**

.. code-block:: bash

   # Deploy to real robot
   ros2 launch my_package hardware.launch.py
   # Tune for real-world performance, collect data

**Week 5+: Refinement**

- Iterate on hardware tuning
- Add robustness features
- Extend to new tasks
- Document findings

Summary
=======

**The dynamicalnodes Hardware Deployment Philosophy**:

✓ **Same Code**: Controller/estimator logic unchanged across platforms
✓ **Different Sources**: Software → Gazebo → Hardware provide /odom
✓ **Gradual Transition**: Test thoroughly at each stage before advancing
✓ **Safety First**: Conservative parameters, emergency stops, supervision
✓ **Expect Differences**: Hardware is harder - that's why we simulate first!

**Deployment Checklist**:

- [ ] Software simulation works perfectly
- [ ] Gazebo simulation matches software
- [ ] Hardware prerequisites met (charged, configured, network)
- [ ] Safety measures in place (emergency stop, clear area)
- [ ] Launch files modified for hardware (remove Gazebo, update topics)
- [ ] Parameters tuned conservatively for first hardware test
- [ ] Monitoring tools ready (rqt_graph, topic echo, bag recording)
- [ ] Short test plan prepared (5-10 seconds initially)
- [ ] Human supervisor present

**Next Steps**:

- Deploy your TurtleBot/Crazyflie system to hardware
- Compare performance: simulation vs reality
- Iterate on tuning for real-world robustness
- Extend to more complex tasks
- Publish your results!

:doc:`← ROS to Gazebo <index>`
