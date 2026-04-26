================
Getting Started
================

``dynamicalnodes`` is a Python package that serves as a bridge between theoretical control/estimation algorithms and their implementation onto hardware.  

.. container:: graphviz-tight

   .. graphviz::
      :align: center

      digraph GettingStartedFlow {
          rankdir=LR;
          bgcolor="transparent";
          splines=ortho;

          node [
            shape=box,
            style="rounded,filled",
            fillcolor="white",
            color="black",
            fontname="Helvetica",
            fontsize=12,
            margin="0.12,0.08"
          ];

          edge [
            color="black",
            penwidth=1.5,
            arrowsize=0.8
          ];

          Theory [label="Theory"];
          Python [label="Python"];
          ROS    [label="ROS"];
          Gazebo [label="Gazebo"];

          Theory -> Python -> ROS -> Gazebo;
      }

To get started modeling algorithms in ``dynamicalnodes``, read the "Overview" and "Theory to Python" sections. To implement these algorithms into ROS and/or Gazebo, also read the "Python to ROS" and "ROS to Gazebo" sections.


..  toctree::
    :caption: Tutorial
    :maxdepth: 2

    overview
    ./theory_to_python/index
    ./python_to_ros/index
    ./ros_to_gazebo/index
    ./contributing/index
