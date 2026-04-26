:doc:`← Python to ROS <index>`

=====================
Advanced ROS Features
=====================

This guide covers advanced ROS2 features for building production-quality robotics systems with ``dynamicalnodes``.

.. contents:: Quick Navigation
   :local:
   :depth: 2

Overview
========

The core tutorials showed basic ROS integration: topics, nodes, and message conversion. This guide covers:

- **Transforms (tf/tf2)**: Coordinate frame management
- **ROS Bags**: Data recording and playback
- **Multi-Robot Systems**: Namespaces and multiple nodes
- **Visualization (RViz2)**: 3D visualization of robot state
- **Quality of Service (QoS)**: Reliable communication tuning
- **Parameter Server**: Dynamic configuration
- **Actions**: Long-running tasks with feedback

Transform Frames (tf/tf2)
==========================

Why Transforms Matter
---------------------

Robotics systems have multiple coordinate frames:

- **world**: Global reference frame
- **odom**: Odometry frame (drift over time)
- **base_link**: Robot body frame
- **sensor_frame**: Camera, LiDAR, IMU frames

**Problem**: Sensor data arrives in sensor frame, controller needs world frame.

**Solution**: tf/tf2 automatically transforms between frames.

Understanding the Transform Tree
---------------------------------

Typical TurtleBot3 transform tree:

::

   world
     └─ odom
          └─ base_footprint
               └─ base_link
                    ├─ imu_link
                    ├─ camera_link
                    └─ laser_link

**Reading the tree**:

- ``world → odom``: Localization correction (e.g., from AMCL)
- ``odom → base_footprint``: Odometry integration
- ``base_link → sensor_link``: Fixed sensor mounting

Using tf2 in Python
-------------------

**Install**:

.. code-block:: bash

   sudo apt install ros-humble-tf2-ros ros-humble-tf2-geometry-msgs

**Basic transform lookup**:

.. code-block:: python

   import rclpy
   from rclpy.node import Node
   from tf2_ros import TransformListener, Buffer
   from geometry_msgs.msg import TransformStamped
   
   class TransformUser(Node):
       def __init__(self):
           super().__init__('transform_user')
           
           # Create buffer and listener
           self.tf_buffer = Buffer()
           self.tf_listener = TransformListener(self.tf_buffer, self)
       
       def get_transform(self, target_frame, source_frame):
           """Get transform from source to target frame."""
           try:
               # Wait up to 1 second for transform
               transform = self.tf_buffer.lookup_transform(
                   target_frame,
                   source_frame,
                   rclpy.time.Time(),  # Latest available
                   timeout=rclpy.duration.Duration(seconds=1.0)
               )
               return transform
           except Exception as e:
               self.get_logger().error(f'Transform lookup failed: {e}')
               return None

**Transform a point**:

.. code-block:: python

   from tf2_geometry_msgs import do_transform_point
   from geometry_msgs.msg import PointStamped
   
   def transform_point(self, point_in_sensor_frame):
       """Transform point from sensor frame to world frame."""
       
       # Create stamped point
       point_stamped = PointStamped()
       point_stamped.header.frame_id = 'camera_link'
       point_stamped.header.stamp = self.get_clock().now().to_msg()
       point_stamped.point.x = point_in_sensor_frame[0]
       point_stamped.point.y = point_in_sensor_frame[1]
       point_stamped.point.z = point_in_sensor_frame[2]
       
       # Get transform
       transform = self.get_transform('world', 'camera_link')
       
       # Apply transform
       point_in_world = do_transform_point(point_stamped, transform)
       
       return np.array([
           point_in_world.point.x,
           point_in_world.point.y,
           point_in_world.point.z
       ])

Publishing Transforms
---------------------

If your ``dynamicalnodes`` estimator produces pose estimates, publish them as transforms:

.. code-block:: python

   from tf2_ros import TransformBroadcaster
   from geometry_msgs.msg import TransformStamped
   
   class EstimatorWithTF(Node):
       def __init__(self):
           super().__init__('estimator_tf')
           self.tf_broadcaster = TransformBroadcaster(self)
       
       def publish_estimate_as_tf(self, position, quaternion):
           """Publish estimated pose as transform."""
           
           t = TransformStamped()
           t.header.stamp = self.get_clock().now().to_msg()
           t.header.frame_id = 'world'
           t.child_frame_id = 'base_link_estimated'
           
           t.transform.translation.x = position[0]
           t.transform.translation.y = position[1]
           t.transform.translation.z = position[2]
           
           t.transform.rotation.x = quaternion[0]
           t.transform.rotation.y = quaternion[1]
           t.transform.rotation.z = quaternion[2]
           t.transform.rotation.w = quaternion[3]
           
           self.tf_broadcaster.sendTransform(t)

Integrating tf2 with dynamicalnodes
---------------------------

Since ``ROSNode`` doesn't natively support tf2, use a wrapper:

.. code-block:: python

   class PykalNodeWithTF:
       def __init__(self, dynamicalnodes_node):
           self.dynamicalnodes_node = dynamicalnodes_node
           self.tf_buffer = Buffer()
           self.tf_listener = TransformListener(self.tf_buffer, dynamicalnodes_node._node)
       
       def create_node(self):
           self.dynamicalnodes_node.create_node()
       
       def start(self):
           self.dynamicalnodes_node.start()
       
       def lookup_transform(self, target, source):
           return self.tf_buffer.lookup_transform(target, source, rclpy.time.Time())

ROS Bags: Recording and Replay
===============================

Why Use Bags?
-------------

ROS bags record topic data to disk for:

- **Debugging**: Replay problematic scenarios
- **Development**: Test without hardware
- **Analysis**: Post-process data in Python
- **Sharing**: Distribute datasets

Recording Bags
--------------

**Basic recording**:

.. code-block:: bash

   # Record specific topics
   ros2 bag record /odom /cmd_vel /estimate
   
   # Record all topics
   ros2 bag record -a
   
   # Save to specific file
   ros2 bag record -o my_experiment /odom /cmd_vel
   
   # Stop with Ctrl+C

**Selective recording**:

.. code-block:: bash

   # Only control-related topics
   ros2 bag record -e "/cmd_*|/odom"
   
   # Exclude image topics (large!)
   ros2 bag record -a -x "/camera/.*"

Playing Back Bags
-----------------

**Basic playback**:

.. code-block:: bash

   # Play at normal speed
   ros2 bag play my_bag
   
   # Play at 2x speed
   ros2 bag play my_bag --rate 2.0
   
   # Play in loop
   ros2 bag play my_bag --loop
   
   # Start paused (press space to start)
   ros2 bag play my_bag --start-paused

**Remap topics during playback**:

.. code-block:: bash

   # Replay /odom as /odom_recorded
   ros2 bag play my_bag --remap /odom:=/odom_recorded

Analyzing Bags in Python
-------------------------

.. code-block:: python

   from rosbag2_py import SequentialReader, StorageOptions, ConverterOptions
   from rclpy.serialization import deserialize_message
   from rosidl_runtime_py.utilities import get_message
   import numpy as np
   
   def extract_odom_data(bag_path):
       """Extract odometry data from bag file."""
       
       # Setup reader
       storage_options = StorageOptions(uri=bag_path, storage_id='sqlite3')
       converter_options = ConverterOptions(
           input_serialization_format='cdr',
           output_serialization_format='cdr'
       )
       
       reader = SequentialReader()
       reader.open(storage_options, converter_options)
       
       # Get topic metadata
       topic_types = reader.get_all_topics_and_types()
       type_map = {t.name: t.type for t in topic_types}
       
       # Extract messages
       odom_data = []
       while reader.has_next():
           topic, data, timestamp = reader.read_next()
           
           if topic == '/odom':
               msg_type = get_message(type_map[topic])
               msg = deserialize_message(data, msg_type)
               
               odom_data.append({
                   'timestamp': timestamp * 1e-9,  # Convert to seconds
                   'x': msg.pose.pose.position.x,
                   'y': msg.pose.pose.position.y,
                   'vx': msg.twist.twist.linear.x,
                   'vy': msg.twist.twist.linear.y
               })
       
       return np.array([(d['timestamp'], d['x'], d['y'], d['vx'], d['vy']) 
                        for d in odom_data])

**Plotting bag data**:

.. code-block:: python

   import matplotlib.pyplot as plt
   
   # Extract data
   odom = extract_odom_data('my_experiment')
   
   # Plot trajectory
   plt.figure(figsize=(10, 5))
   plt.subplot(1, 2, 1)
   plt.plot(odom[:, 1], odom[:, 2])
   plt.xlabel('X (m)')
   plt.ylabel('Y (m)')
   plt.title('Robot Trajectory')
   plt.axis('equal')
   
   # Plot velocity
   plt.subplot(1, 2, 2)
   plt.plot(odom[:, 0], odom[:, 3], label='vx')
   plt.plot(odom[:, 0], odom[:, 4], label='vy')
   plt.xlabel('Time (s)')
   plt.ylabel('Velocity (m/s)')
   plt.legend()
   plt.title('Robot Velocity')
   
   plt.tight_layout()
   plt.show()

Multi-Robot Systems
===================

Using Namespaces
----------------

Run multiple robots without topic conflicts:

.. code-block:: python

   # Robot 1 nodes
   robot1_controller = ROSNode(
       node_name='controller',
       namespace='robot1',  # Topics become /robot1/cmd_vel, etc.
       callback=controller_callback,
       subscribes_to=[('/odom', Odometry, 'odom')],  # Becomes /robot1/odom
       publishes_to=[('cmd_vel', Twist, '/cmd_vel')],  # Becomes /robot1/cmd_vel
       rate_hz=10.0
   )
   
   # Robot 2 nodes
   robot2_controller = ROSNode(
       node_name='controller',
       namespace='robot2',
       callback=controller_callback,
       subscribes_to=[('/odom', Odometry, 'odom')],
       publishes_to=[('cmd_vel', Twist, '/cmd_vel')],
       rate_hz=10.0
   )

**Note**: ``dynamicalnodes``'s ``ROSNode`` doesn't natively support namespaces. You need to modify topic names manually:

.. code-block:: python

   # Workaround: Include namespace in topic names
   robot1_controller = ROSNode(
       node_name='robot1_controller',
       callback=controller_callback,
       subscribes_to=[('/robot1/odom', Odometry, 'odom')],
       publishes_to=[('cmd_vel', Twist, '/robot1/cmd_vel')],
       rate_hz=10.0
   )

Multi-Robot Coordination
-------------------------

Share information between robots:

.. code-block:: python

   def robot1_callback(tk, robot1_odom, robot2_odom):
       """Controller that considers other robot's position."""
       
       # Extract positions
       my_pos = robot1_odom[:2]
       other_pos = robot2_odom[:2]
       
       # Avoid collision
       distance = np.linalg.norm(my_pos - other_pos)
       if distance < 0.5:  # Too close!
           # Compute repulsive force
           repulsion = (my_pos - other_pos) / distance
       else:
           repulsion = np.zeros(2)
       
       # Navigate to goal + avoid other robot
       goal = np.array([5.0, 5.0])
       attraction = (goal - my_pos) / np.linalg.norm(goal - my_pos)
       
       velocity = attraction + repulsion
       
       return {'cmd_vel': np.concatenate([velocity, [0, 0, 0, 0]])}
   
   # Node subscribes to both robots' odometry
   robot1_node = ROSNode(
       node_name='robot1_controller',
       callback=robot1_callback,
       subscribes_to=[
           ('/robot1/odom', Odometry, 'robot1_odom'),
           ('/robot2/odom', Odometry, 'robot2_odom')
       ],
       publishes_to=[('cmd_vel', Twist, '/robot1/cmd_vel')],
       rate_hz=10.0
   )

Visualization with RViz2
========================

Launch RViz2
------------

.. code-block:: bash

   # Launch RViz
   rviz2
   
   # Or with config file
   rviz2 -d my_config.rviz

Common Display Types
--------------------

**Odometry**:

1. Add → By topic → /odom → Odometry
2. Shows robot pose as axes

**Path**:

.. code-block:: python

   # Publish Path message for trajectory visualization
   from nav_msgs.msg import Path
   from geometry_msgs.msg import PoseStamped
   
   def publish_path(self, positions):
       path = Path()
       path.header.frame_id = 'world'
       path.header.stamp = self.get_clock().now().to_msg()
       
       for pos in positions:
           pose = PoseStamped()
           pose.header = path.header
           pose.pose.position.x = pos[0]
           pose.pose.position.y = pos[1]
           pose.pose.position.z = pos[2]
           path.poses.append(pose)
       
       self.path_publisher.publish(path)

**Markers** (custom visualization):

.. code-block:: python

   from visualization_msgs.msg import Marker
   
   def publish_goal_marker(self, goal_position):
       marker = Marker()
       marker.header.frame_id = 'world'
       marker.header.stamp = self.get_clock().now().to_msg()
       marker.type = Marker.SPHERE
       marker.action = Marker.ADD
       
       marker.pose.position.x = goal_position[0]
       marker.pose.position.y = goal_position[1]
       marker.pose.position.z = goal_position[2]
       
       marker.scale.x = 0.2
       marker.scale.y = 0.2
       marker.scale.z = 0.2
       
       marker.color.r = 1.0
       marker.color.g = 0.0
       marker.color.b = 0.0
       marker.color.a = 1.0
       
       self.marker_publisher.publish(marker)

Quality of Service (QoS)
=========================

Why QoS Matters
---------------

Different scenarios need different reliability:

- **Real-time control**: Latest data, drop old messages
- **Logging**: Reliable delivery, no drops
- **Diagnostics**: Best effort, don't block

QoS Profiles
------------

.. code-block:: python

   from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy, HistoryPolicy
   
   # Sensor data (latest only)
   sensor_qos = QoSProfile(
       reliability=ReliabilityPolicy.BEST_EFFORT,
       durability=DurabilityPolicy.VOLATILE,
       history=HistoryPolicy.KEEP_LAST,
       depth=1
   )
   
   # Control commands (reliable)
   command_qos = QoSProfile(
       reliability=ReliabilityPolicy.RELIABLE,
       durability=DurabilityPolicy.VOLATILE,
       history=HistoryPolicy.KEEP_LAST,
       depth=10
   )
   
   # Logged data (persistent)
   logging_qos = QoSProfile(
       reliability=ReliabilityPolicy.RELIABLE,
       durability=DurabilityPolicy.TRANSIENT_LOCAL,
       history=HistoryPolicy.KEEP_ALL
   )

**Note**: ``dynamicalnodes``'s ``ROSNode`` doesn't expose QoS settings. You'd need to modify the source or create publishers/subscribers manually.

Matching QoS
------------

Publishers and subscribers must have compatible QoS:

.. code-block:: bash

   # Check QoS of existing topic
   ros2 topic info /odom --verbose
   
   # Output shows:
   # Reliability: RELIABLE / BEST_EFFORT
   # Durability: VOLATILE / TRANSIENT_LOCAL

**Common issue**: Gazebo publishes with BEST_EFFORT, your subscriber uses RELIABLE → no connection!

**Solution**: Match publisher's QoS.

Parameter Server
================

Dynamic Parameters
------------------

Change node behavior without restarting:

.. code-block:: python

   from rcl_interfaces.msg import ParameterDescriptor
   
   class ParameterizedNode(Node):
       def __init__(self):
           super().__init__('param_node')
           
           # Declare parameters
           self.declare_parameter('kp', 1.0, 
               ParameterDescriptor(description='Proportional gain'))
           self.declare_parameter('kd', 0.5,
               ParameterDescriptor(description='Derivative gain'))
           
           # Read parameters
           self.kp = self.get_parameter('kp').value
           self.kd = self.get_parameter('kd').value
           
           # Add callback for parameter changes
           self.add_on_set_parameters_callback(self.parameter_callback)
       
       def parameter_callback(self, params):
           for param in params:
               if param.name == 'kp':
                   self.kp = param.value
                   self.get_logger().info(f'Kp updated to {self.kp}')
               elif param.name == 'kd':
                   self.kd = param.value
                   self.get_logger().info(f'Kd updated to {self.kd}')
           return SetParametersResult(successful=True)

**Set parameters from command line**:

.. code-block:: bash

   # Set parameter
   ros2 param set /param_node kp 2.0
   
   # Get parameter
   ros2 param get /param_node kp
   
   # List all parameters
   ros2 param list

**Load from YAML file**:

.. code-block:: yaml

   # config/params.yaml
   param_node:
     ros__parameters:
       kp: 1.5
       kd: 0.3

.. code-block:: bash

   ros2 run my_package my_node --ros-args --params-file config/params.yaml

Actions (Long-Running Tasks)
=============================

When to Use Actions
-------------------

Actions are for tasks with:

- Duration > 1 second
- Intermediate feedback needed
- Cancellation support

**Examples**:

- Navigate to waypoint (feedback: distance remaining)
- Trajectory following (feedback: current segment)
- Object manipulation (feedback: grasp progress)

Action Client Example
---------------------

.. code-block:: python

   from rclpy.action import ActionClient
   from nav2_msgs.action import NavigateToPose
   
   class NavigationClient(Node):
       def __init__(self):
           super().__init__('nav_client')
           self.action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
       
       def send_goal(self, x, y, theta):
           goal_msg = NavigateToPose.Goal()
           goal_msg.pose.header.frame_id = 'map'
           goal_msg.pose.pose.position.x = x
           goal_msg.pose.pose.position.y = y
           # ... set orientation from theta
           
           self.action_client.wait_for_server()
           
           send_goal_future = self.action_client.send_goal_async(
               goal_msg,
               feedback_callback=self.feedback_callback
           )
           send_goal_future.add_done_callback(self.goal_response_callback)
       
       def feedback_callback(self, feedback_msg):
           feedback = feedback_msg.feedback
           self.get_logger().info(f'Distance remaining: {feedback.distance_remaining:.2f}m')
       
       def goal_response_callback(self, future):
           goal_handle = future.result()
           if not goal_handle.accepted:
               self.get_logger().info('Goal rejected')
               return
           
           self.get_logger().info('Goal accepted')
           result_future = goal_handle.get_result_async()
           result_future.add_done_callback(self.result_callback)
       
       def result_callback(self, future):
           result = future.result().result
           self.get_logger().info('Navigation complete!')

Best Practices
==============

1. **Use tf2 for all coordinate transforms**

   - Don't manually transform between frames
   - Let tf2 handle the math and timing

2. **Record bags for every experiment**

   - Invaluable for debugging
   - Essential for reproducible research

3. **Match QoS profiles**

   - Check existing topic QoS before subscribing
   - Use RELIABLE for critical data, BEST_EFFORT for high-rate sensors

4. **Parameterize everything**

   - Controller gains, filter noise, rates
   - Use YAML config files

5. **Visualize with RViz**

   - See what the robot sees
   - Debug transform trees
   - Verify sensor data

6. **Namespace multi-robot systems**

   - Prevents topic conflicts
   - Enables scaling to N robots

Summary
=======

**Advanced Features Covered**:

✓ **tf/tf2**: Coordinate frame transformations  
✓ **ROS Bags**: Recording, playback, analysis
✓ **Multi-Robot**: Namespaces and coordination
✓ **RViz2**: 3D visualization
✓ **QoS**: Communication reliability tuning
✓ **Parameters**: Dynamic configuration
✓ **Actions**: Long-running tasks with feedback

**Integration with dynamicalnodes**:

- Most features require extending ``ROSNode`` or using native ROS2 nodes
- tf2, bags, and RViz work seamlessly with dynamicalnodes nodes
- Parameters and QoS need custom wrappers

**Next Steps**:

- Implement multi-robot coordination in dynamicalnodes
- Record experimental data with bags
- Create custom RViz displays for your system
- Build action servers for complex tasks

:doc:`← Python to ROS <index>`
