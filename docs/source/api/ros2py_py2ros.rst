ros2py_py2ros
=============

Message conversion functions. Each ROS message type has a ``ros2py_<type>`` /
``py2ros_<type>`` pair; pass them to a :class:`~dynamicalnodes.rosnode.ROSNode`
through the ``"ros2py"`` and ``"py2ros"`` keys of its ``subs``/``pubs`` entries.

.. note::

   Importing this module requires a ROS2 installation (it imports ``rclpy`` and
   the ROS message packages at module level). These docs are built with those
   imports mocked.

.. automodule:: dynamicalnodes.ros2py_py2ros
   :members:
   :undoc-members:
   :show-inheritance:
