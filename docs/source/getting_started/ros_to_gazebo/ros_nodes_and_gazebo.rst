:doc:`← ROS to Gazebo <index>`

======================
 ROS Nodes and Gazebo
======================

This section demonstrates how to integrate the ROS nodes you created in the "Python to ROS" section with Gazebo simulation environments. By using ``dynamicalnodes.gazebo`` wrappers, you can test your control systems in realistic simulated environments before deploying to hardware.

"Example: Turtlebot Gazebo Integration" shows how to modify the Turtlebot ROS node architecture to interface with a Gazebo-simulated Turtlebot, including topic remapping and simulation-specific configurations.

"Example: Crazyflie Gazebo Integration" demonstrates integrating the multi-sensor Crazyflie system with a Gazebo physics simulation, handling simulated IMU, position, and velocity data.

..  toctree::
    :maxdepth: 2

    ../../notebooks/tutorial/ros_to_gazebo/turtlebot_gazebo_integration.ipynb
    ../../notebooks/tutorial/ros_to_gazebo/crazyflie_gazebo_integration.ipynb

:doc:`← ROS to Gazebo <index>`
