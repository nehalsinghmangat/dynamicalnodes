:doc:`← Python to ROS <index>`

=========
 Modules
=========

This section consists of tips, tricks, and usage examples of the ``dynamicalnodes.ROSNode`` and ``dynamicalnodes.ros2py_py2ros`` modules. The following notebooks are a complement to the API reference and it is recommended to have both at hand (e.g. in an open tab) while you are developing with ``dynamicalnodes``.

"ROSNode" covers the core wrapper class that transforms Python callbacks into ROS2 nodes, including subscription/publication configuration, staleness policies, and node lifecycle management.

"ROS2PY and PY2ROS" explains the message conversion system that automatically translates between ROS message types and NumPy arrays, including how to register custom message types.

"Custom Messages" provides guidance on working with custom ROS message types beyond the standard message library.

..  toctree::
    :maxdepth: 2

    ../../notebooks/tutorial/python_to_ros/ros_node
    ../../notebooks/tutorial/python_to_ros/ros2py_py2ros

:doc:`← Python to ROS <index>`    
