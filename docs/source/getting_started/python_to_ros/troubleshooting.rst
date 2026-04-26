:doc:`← Python to ROS <index>`

==============================
Troubleshooting Common Issues
==============================

This guide covers common issues when working with ``dynamicalnodes``, ROS2, and Gazebo, along with their solutions.

.. contents:: Quick Navigation
   :local:
   :depth: 2

ROS2 Node Issues
================

Node Not Publishing
-------------------

**Problem**: Created ROSNode but no data appears on topic.

**Symptoms**:

.. code-block:: bash

   ros2 topic list  # Shows topic exists
   ros2 topic echo /my_topic  # No output

**Common Causes**:

1. **Forgot to call** ``create_node()`` **before** ``start()``

   .. code-block:: python

      # WRONG
      node = ROSNode(...)
      node.start()  # ERROR: Node not created yet!
      
      # CORRECT
      node = ROSNode(...)
      node.create_node()
      node.start()

2. **Callback not returning dictionary**

   .. code-block:: python

      # WRONG
      def callback(tk):
          result = compute_something()
          return result  # Must be dict!
      
      # CORRECT
      def callback(tk):
          result = compute_something()
          return {'output': result}

3. **Return key doesn't match publishes_to**

   .. code-block:: python

      # WRONG
      publishes_to=[('estimate', Odometry, '/estimate')]
      return {'state': x}  # Key mismatch!
      
      # CORRECT
      publishes_to=[('estimate', Odometry, '/estimate')]
      return {'estimate': x}

4. **Message converter not registered**

   Check if your message type is in ``PY2ROS_DEFAULT`` registry:

   .. code-block:: python

      from dynamicalnodes.ros.ros2py_py2ros import PY2ROS_DEFAULT
      from geometry_msgs.msg import Twist
      
      # Check if converter exists
      if Twist in PY2ROS_DEFAULT:
          print("Converter registered!")
      else:
          print("Need to register custom converter")

**Solution**: Verify node creation sequence and return value format.

Node Not Receiving Messages
----------------------------

**Problem**: Node created but callback never receives subscribed topics.

**Symptoms**:

.. code-block:: python

   def callback(tk, odom):
       print(f"Received: {odom}")  # Never prints!

**Common Causes**:

1. **Topic name mismatch**

   .. code-block:: bash

      # Check if publisher exists
      ros2 topic list
      ros2 topic info /odom  # Check publishers
      
      # Check your subscription
      subscribes_to=[('/odom', Odometry, 'odom')]  # Must match!

2. **QoS incompatibility** (most common!)

   .. code-block:: python

      # Some nodes publish with TRANSIENT_LOCAL
      # Default subscriber uses VOLATILE
      
      # Solution: Match QoS settings
      from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
      
      qos = QoSProfile(
          reliability=ReliabilityPolicy.RELIABLE,
          durability=DurabilityPolicy.TRANSIENT_LOCAL,
          depth=10
      )
      
      # Then use when creating subscriber (requires ROSNode modification)

3. **Callback argument name mismatch**

   .. code-block:: python

      # WRONG
      subscribes_to=[('/odom', Odometry, 'odom')]
      def callback(tk, odometry):  # Name doesn't match!
          pass
      
      # CORRECT
      subscribes_to=[('/odom', Odometry, 'odom')]
      def callback(tk, odom):  # Must match 'odom'!
          pass

4. **Message converter not registered**

   .. code-block:: python

      from dynamicalnodes.ros.ros2py_py2ros import ROS2PY_DEFAULT
      from sensor_msgs.msg import Imu
      
      # Check if converter exists
      if Imu in ROS2PY_DEFAULT:
          print("Converter registered!")
      else:
          print("Need to register custom converter")

**Solution**: Verify topic names, QoS settings, and argument names.

Message Conversion Errors
=========================

"No converter registered" Error
--------------------------------

**Problem**: 

.. code-block:: python

   KeyError: <class 'custom_msgs.msg.MyMessage'>

**Cause**: Custom message type not in converter registries.

**Solution**: Register custom converters:

.. code-block:: python

   from dynamicalnodes.ros.ros2py_py2ros import ROS2PY_DEFAULT, PY2ROS_DEFAULT
   from custom_msgs.msg import MyMessage
   import numpy as np
   
   # ROS → NumPy converter
   def my_message_to_numpy(msg):
       return np.array([msg.x, msg.y, msg.z])
   
   # NumPy → ROS converter
   def numpy_to_my_message(arr):
       msg = MyMessage()
       msg.x = float(arr[0])
       msg.y = float(arr[1])
       msg.z = float(arr[2])
       return msg
   
   # Register converters
   ROS2PY_DEFAULT[MyMessage] = my_message_to_numpy
   PY2ROS_DEFAULT[MyMessage] = numpy_to_my_message

**See**: :doc:`Custom Message Types Tutorial <custom_messages>` for full guide.

"Array shape mismatch" Error
-----------------------------

**Problem**:

.. code-block:: python

   ValueError: cannot reshape array of size 12 into shape (13,)

**Cause**: Callback returns NumPy array with wrong size for message type.

**Example**:

.. code-block:: python

   # Odometry expects 13 elements: [x, y, z, qx, qy, qz, qw, vx, vy, vz, wx, wy, wz]
   
   # WRONG
   return {'estimate': np.array([x, y, z])}  # Only 3 elements!
   
   # CORRECT
   pose = np.array([x, y, z, 0, 0, 0, 1])      # 7: position + quaternion
   twist = np.array([vx, vy, vz, 0, 0, 0])      # 6: linear + angular vel
   return {'estimate': np.concatenate([pose, twist])}  # 13 elements

**Solution**: Check expected message format in converter function.

Gazebo Integration Issues
==========================

"No /odom topic" After Starting Gazebo
---------------------------------------

**Problem**: Gazebo launches but no odometry published.

**Symptoms**:

.. code-block:: bash

   ros2 topic list  # /odom missing

**Common Causes**:

1. **Wrong robot model** in ``start_gazebo()``

   .. code-block:: python

      # WRONG
      gz = start_gazebo(robot='turtlebot4')  # Not supported!
      
      # CORRECT
      gz = start_gazebo(robot='turtlebot3')  # Supported

2. **Robot not spawned yet**

   Gazebo takes 5-10 seconds to spawn robot. Wait before checking topics:

   .. code-block:: python

      import time
      gz = start_gazebo(robot='turtlebot3')
      time.sleep(10)  # Wait for spawn
      
      # Now check
      !ros2 topic list

3. **GAZEBO_MODEL_PATH not set**

   .. code-block:: bash

      # Check if model path includes turtlebot3_gazebo
      echo $GAZEBO_MODEL_PATH
      
      # Fix: Source ROS2 workspace
      source /opt/ros/humble/setup.bash
      source ~/turtlebot3_ws/install/setup.bash

**Solution**: Use supported robots, wait for spawn, check environment variables.

Gazebo Crashes with "libGL error"
----------------------------------

**Problem**: Gazebo crashes immediately with OpenGL error.

**Error**:

.. code-block:: text

   libGL error: failed to load driver: swrast

**Cause**: Missing graphics drivers or running headless.

**Solution**: Use headless mode in Jupyter notebooks:

.. code-block:: python

   gz = start_gazebo(robot='turtlebot3', headless=True)

Or install proper graphics drivers:

.. code-block:: bash

   sudo apt install mesa-utils libgl1-mesa-glx

Robot Doesn't Move in Gazebo
-----------------------------

**Problem**: Publishing to ``/cmd_vel`` but robot stationary.

**Diagnostic**:

.. code-block:: bash

   # Check if commands are being published
   ros2 topic echo /cmd_vel
   
   # Check if Gazebo is receiving them
   ros2 topic info /cmd_vel  # Should show 2+ subscriptions

**Common Causes**:

1. **Wrong topic name**

   .. code-block:: bash

      # TurtleBot3 uses /cmd_vel
      # Some robots use /mobile_base/commands/velocity
      
      # Check with
      ros2 topic list | grep cmd

2. **Message format wrong**

   .. code-block:: python

      # WRONG: Only linear velocity
      return {'cmd_vel': np.array([v])}
      
      # CORRECT: Linear + angular velocity
      return {'cmd_vel': np.array([v, 0, 0, 0, 0, omega])}

3. **QoS mismatch** (rare but possible)

   .. code-block:: bash

      ros2 topic info /cmd_vel  # Check QoS profiles

**Solution**: Verify topic name, message format, and QoS settings.

Time Synchronization Issues
============================

"use_sim_time" Warning
-----------------------

**Problem**:

.. code-block:: text

   [WARN] Parameter use_sim_time not set, defaulting to false

**Cause**: Gazebo uses simulation time, but nodes use wall-clock time.

**Impact**: Inconsistent timestamps, tf transforms may fail.

**Solution**: Set ``use_sim_time`` parameter:

.. code-block:: python

   # Option 1: In ROSNode creation
   node._node.declare_parameter('use_sim_time', True)
   
   # Option 2: Launch file
   Node(
       package='my_package',
       executable='my_node',
       parameters=[{'use_sim_time': True}]
   )
   
   # Option 3: Command line
   ros2 run my_package my_node --ros-args -p use_sim_time:=true

Timestamps in Future
--------------------

**Problem**:

.. code-block:: text

   [WARN] Message from future! stamp=1234.5, now=1234.0

**Cause**: Mixing simulation time and wall-clock time.

**Solution**: Ensure **all nodes** use ``use_sim_time: true`` when using Gazebo.

Callback Rate Issues
====================

Callback Running Too Slow
--------------------------

**Problem**: Set ``rate_hz=100`` but callback only runs at 10 Hz.

**Diagnostic**:

.. code-block:: python

   def callback(tk):
       print(f"Time: {tk:.3f}")  # Check timestamps
       # ... rest of callback

**Common Causes**:

1. **Callback too expensive**

   .. code-block:: python

      def callback(tk, image):
          # Processing 1920x1080 image at 100 Hz? Impossible!
          result = expensive_cv2_operation(image)

   **Solution**: Reduce rate or optimize computation.

2. **Blocking I/O in callback**

   .. code-block:: python

      # WRONG
      def callback(tk):
          data = requests.get('http://slow-api.com')  # Blocks!
          return {'output': data}
      
      # CORRECT: Use async or background thread
      def callback(tk):
          # Return cached data, update in background
          return {'output': cached_data}

3. **GIL contention** (if using multiple Python threads)

   **Solution**: Use multiprocessing or C++ nodes for high-rate nodes.

**Solution**: Profile callback, reduce computation, or lower rate.

Callback Not Running
--------------------

**Problem**: Node created and started, but callback never executes.

**Diagnostic**:

.. code-block:: python

   def callback(tk):
       print("CALLBACK RUNNING!")  # Never prints
       return {'output': np.zeros(3)}

**Common Causes**:

1. **Forgot to call** ``start()``

   .. code-block:: python

      node = ROSNode(...)
      node.create_node()
      # Missing: node.start()

2. **No executor running**

   .. code-block:: python

      # WRONG
      node.create_node()
      node.start()
      # Program exits immediately!
      
      # CORRECT
      node.create_node()
      node.start()
      rclpy.spin(node._node)  # Keeps running

3. **Stale message policy dropping data**

   .. code-block:: python

      # If no messages received, callback won't run with 'drop' policy
      stale_config={'odom': {'after': 0.1, 'policy': 'drop'}}
      
      # Solution: Use 'zero' or 'hold' during testing
      stale_config={'odom': {'after': 0.1, 'policy': 'zero'}}

**Solution**: Ensure ``start()`` is called and executor is spinning.

DynamicalSystem Issues
=======================

"state_name required" Error
----------------------------

**Problem**:

.. code-block:: python

   ValueError: If f is provided, state_name must also be provided

**Cause**: Created DynamicalSystem with ``f`` but no ``state_name``.

**Solution**:

.. code-block:: python

   # WRONG
   plant = DynamicalSystem(
       f=my_dynamics,
       h=my_observation
   )
   
   # CORRECT
   plant = DynamicalSystem(
       f=my_dynamics,
       h=my_observation,
       state_name='x'
   )

State Not Updating
------------------

**Problem**: Calling ``step()`` but state doesn't change.

**Cause**: ``f`` function not using parameters from ``param_dict``.

**Example**:

.. code-block:: python

   # WRONG
   x_internal = np.array([0, 0, 0])
   
   def f(x, u):
       global x_internal
       x_internal = x_internal + u  # Using global, not param_dict!
       return x_internal
   
   # CORRECT
   def f(x, u):
       return x + u  # Returns new state, stored in param_dict

**Solution**: Ensure ``f`` is pure function returning new state.

Parameter Binding Issues
========================

"Missing required parameter" Error
-----------------------------------

**Problem**:

.. code-block:: python

   TypeError: callback() missing 1 required positional argument: 'u'

**Cause**: Callback function expects parameter not in ``param_dict``.

**Diagnostic**:

.. code-block:: python

   def callback(tk, x, u):  # Expects 'u'
       return {'output': compute(x, u)}
   
   param_dict = {'x': np.zeros(3)}  # No 'u'!

**Solution**: Add missing parameter to ``param_dict``:

.. code-block:: python

   param_dict = {
       'x': np.zeros(3),
       'u': np.zeros(2)  # Add this
   }

Unexpected Parameter Ignored
-----------------------------

**Problem**: Added parameter to ``param_dict`` but function doesn't use it.

**Example**:

.. code-block:: python

   def my_function(x):  # Only expects 'x'
       return x + 1
   
   param_dict = {
       'x': np.array([1, 2, 3]),
       'noise': np.array([0.1, 0.1, 0.1])  # Ignored!
   }

**Cause**: ``_smart_call()`` only binds parameters that match function signature.

**Solution**: This is **expected behavior**. Unused parameters are safely ignored.

Debugging Strategies
====================

Enable Verbose Logging
----------------------

.. code-block:: python

   import logging
   logging.basicConfig(level=logging.DEBUG)
   
   # Now see detailed logs from dynamicalnodes

Check ROS Topic Communication
------------------------------

.. code-block:: bash

   # List all topics
   ros2 topic list
   
   # Check topic details
   ros2 topic info /odom
   
   # Echo topic data
   ros2 topic echo /odom
   
   # Check message type
   ros2 interface show nav_msgs/msg/Odometry
   
   # Measure topic rate
   ros2 topic hz /odom

Visualize ROS Graph
-------------------

.. code-block:: bash

   # See node connections
   rqt_graph
   
   # List nodes
   ros2 node list
   
   # Check node info
   ros2 node info /my_node

Test Components Independently
------------------------------

.. code-block:: python

   # Test DynamicalSystem alone
   plant = DynamicalSystem(...)
   param_dict = {'x': x0, 'u': u0}
   result = plant.step(param_dict)
   print(result)  # Verify output
   
   # Test ROSNode with minimal callback
   def simple_callback(tk):
       print(f"Running at {tk}")
       return {'output': np.zeros(3)}
   
   node = ROSNode(
       node_name='test',
       callback=simple_callback,
       subscribes_to=[],
       publishes_to=[('output', Vector3, '/test')],
       rate_hz=1.0
   )

Use Python Debugger
-------------------

.. code-block:: python

   import pdb
   
   def callback(tk, odom):
       pdb.set_trace()  # Breakpoint
       result = process(odom)
       return {'output': result}

Common Error Messages Reference
================================

Quick lookup for common errors:

+------------------------------------------------+----------------------------------+
| Error Message                                  | Solution                         |
+================================================+==================================+
| ``ValueError: state_name required``            | Add ``state_name='x'`` to        |
|                                                | DynamicalSystem                  |
+------------------------------------------------+----------------------------------+
| ``KeyError: <class 'msgs.MyMessage'>``         | Register message converter       |
+------------------------------------------------+----------------------------------+
| ``No converter registered``                    | Add to ROS2PY/PY2ROS registries  |
+------------------------------------------------+----------------------------------+
| ``Array shape mismatch``                       | Check message format size        |
+------------------------------------------------+----------------------------------+
| ``Topic not found``                            | Check topic name with            |
|                                                | ``ros2 topic list``              |
+------------------------------------------------+----------------------------------+
| ``QoS mismatch``                               | Match publisher/subscriber QoS   |
+------------------------------------------------+----------------------------------+
| ``use_sim_time warning``                       | Set ``use_sim_time: true``       |
+------------------------------------------------+----------------------------------+
| ``libGL error``                                | Use ``headless=True`` in Gazebo  |
+------------------------------------------------+----------------------------------+
| ``Callback not running``                       | Call ``start()`` and spin        |
+------------------------------------------------+----------------------------------+
| ``Message from future``                        | Sync simulation time across nodes|
+------------------------------------------------+----------------------------------+

Getting Help
============

If you encounter issues not covered here:

1. **Check documentation**:
   - dynamicalnodes docs: https://dynamicalnodes.readthedocs.io
   - ROS2 docs: https://docs.ros.org/en/humble/

2. **Search existing issues**:
   - GitHub: https://github.com/your-org/dynamicalnodes/issues

3. **Ask for help**:
   - Create new issue with minimal reproducible example
   - Include error messages, code snippets, ROS2 version

4. **Common resources**:
   - ROS Answers: https://answers.ros.org
   - ROS Discourse: https://discourse.ros.org

Summary
=======

**Most Common Issues**:

1. ✗ Forgot ``create_node()`` before ``start()``
2. ✗ Topic name mismatch
3. ✗ QoS incompatibility
4. ✗ Message converter not registered
5. ✗ Callback return format wrong
6. ✗ No executor spinning
7. ✗ Simulation time not synchronized
8. ✗ Gazebo robot not spawned yet

**Debugging Workflow**:

1. Check topic exists: ``ros2 topic list``
2. Check message flow: ``ros2 topic echo /topic``
3. Check connections: ``rqt_graph``
4. Check QoS: ``ros2 topic info /topic``
5. Add print statements to callback
6. Test components independently
7. Use Python debugger

**Best Practices**:

✓ Always call ``create_node()`` before ``start()``
✓ Use ``rqt_graph`` to visualize system
✓ Test DynamicalSystems before wrapping in ROSNode
✓ Register message converters for custom types
✓ Match topic names exactly (case-sensitive)
✓ Set ``use_sim_time: true`` when using Gazebo
✓ Wait for Gazebo spawn before checking topics
✓ Use consistent parameter names in callbacks

:doc:`← Python to ROS <index>`
