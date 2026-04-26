:doc:`← Getting Started <../index>`

=============
ROS to Gazebo
=============

``dynamicalnodes`` takes a back seat in this section and serves only as a wrapper for ``Gazebo``. The point of wrapping ``Gazebo`` is so the entire ``dynamicalnodes`` workflow can stay within a Jupyter notebook (at least in theory). Of course, if you are comfortable with the command line and would prefer interfacing with ``Gazebo`` in that way, you are free to do so with no loss in performance (indeed, you will have far greater flexibility in this way).

The "Installation" section will guide you through installing the ``gazebo`` package.

The "ROS Nodes and Gazebo" section show how the ``ROS`` node architecture we created in the "Python to ROS" section must be modified so that they can interface properly with ``gazebo``.

The "Modules" section offers tips and usage examples of the ``dynamicalnodes.gazebo`` module.

The "Gazebo Tips and Tricks" section serves as a reference for useful ``gazebo`` commands. 

The "Troubleshooting" section offers solutions to common problems when interfacing with Gazebo. 

..  toctree::
    :maxdepth: 2

    installation
    ros_nodes_and_gazebo
    modules
    gazebo_tips_and_tricks
    troubleshooting

:doc:`← Getting Started <../index>`
