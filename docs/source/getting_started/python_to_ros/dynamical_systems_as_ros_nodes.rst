:doc:`← Python to ROS <index>`

================================
 Dynamical Systems as ROS Nodes
================================

This section demonstrates how to deploy the dynamical systems you created in the "Theory to Python" section as ROS2 nodes. Using the ``dynamicalnodes.ROSNode`` wrapper, you can transform Python functions into ROS nodes that communicate via topics.

"Example: Turtlebot ROS Deployment" walks through wrapping the Turtlebot state estimator from the previous section as a ROS node and deploying it to subscribe to real robot topics.

"Example: Crazyflie ROS Deployment" demonstrates a more complex deployment involving multiple sensors and asynchronous data streams for the Crazyflie quadcopter.

..  toctree::
    :maxdepth: 2

    ../../notebooks/tutorial/python_to_ros/cruise_control_ros_deployment	       
    ../../notebooks/tutorial/python_to_ros/turtlebot_ros_deployment
    ../../notebooks/tutorial/python_to_ros/crazyflie_ros_deployment


:doc:`← Python to ROS <index>`

     
