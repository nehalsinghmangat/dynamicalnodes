:doc:`← Getting Started <index>`
     
========
Overview
========
In this section, we will discuss:

- the personal background of the auther 
- a serious problem in robotics
- a proposed solution (hint: it may be ``dynamicalnodes``)
- the structure of the "Tutorial"" and how best to work through it 

Who am I?
=========
My name is Nehal Mangat, and I am a (handsome) graduate student at the University of Nevada, Reno, where I am pursuing a masters in Mechanical Engineering and Applied Mathematics. I am also a robotics research assistant in the `van Breugel lab <https://www.florisvanbreugel.com>`_ and a former intern of the University of Florida's `Autonomous Vehicles Laboratory <https://avl.reef.ufl.edu/>`_. 

I have been involved in the world of academic robotics for several years now. I love my field, but it is a shame to say that there is something rotten in the state of academic robotics. 

The Problem
===========
Academia has witnessed an explosion of control and estimation algorithms. This should be a good thing; certainly we should not be worse off for having more ideas.  

Unfortunately, academia values novelty, not utility; that is, researchers are incentivized to publish novel results at the expense of useability. With little reason to test results in reality, the hardware implementation of an algorithm is passed onto future researchers -- who, pressed to publish novel results of their own, instead extend the algorithm, publish, and pass the buck along to future researchers, *ad infinitum*.

When the day comes that the algorithm is finally implemented onto hardware, and it does not work as expected (or at all), where do we begin troubleshooting? Is it a hardware issue, a software issue, or does the real issue lie in the third paper of this algorithm's journey, where the substitution of a new numerical method lead to unforeseen consequences when faced with asynchronous sensor data? 

This is a tragedy of efficiency, to say nothing of the sanity lost in troubleshooting such issues.


The Solution
============
The ``dynamicalnodes`` package is a Python package designed to make the following transitions as painless as possible:

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


   
`ROS <https://www.ros.org/>`_ and `Gazebo <https://gazebosim.org/home>`_  are mature open-source robotics platforms that have already eased the burden of the last bridge; ``dynamicalnodes`` aims to ease the burden of the first two. How?

``dynamicalnodes`` uses the :doc:`discrete-time dynamical system <../notebooks/tutorial/theory_to_python/dynamical_system>` as a compositional primitive in defining algorithms and control systems. Such representations are modular, easy to implement, and easy to debug, thus spanning the gap between "Theory" and "Python"".

Further, a modular framework induces a simple API between Python and ROS, which lets us abstract away from the CLI and interface with ROS from a Jupyter notebook via ``dynamicalnodes``. In addition to a quality of life improvement, the composition of dynamical systems has a direct correspondence with ``ROS`` node architecturem, making it possible to implement and debug such architecturs in Python before automagically translating them into ``ROS``. Thus, the second bridge from "Python" to "ROS" is spanned. 

Using the Tutorial
==================
The "Tutorial" is split into four sections.

Overview
^^^^^^^^
If you have managed to skip to the end of this one-page overview without reading anything, I recommend scrolling back to the beginning and reading the whole overview.

Theory to Python
^^^^^^^^^^^^^^^^
If you are new to this package and want to try casting algorithms/control systems as dynamical systems, :doc:`start here <./theory_to_python/index>`. 

Python to ROS
^^^^^^^^^^^^^
If you are comfortable using ``dynamicalnodes`` to cast algorithms/control systems as dynamical systems and want to begin simulating things in ``ROS``, :doc:`start here <./python_to_ros/index>`. 

ROS to Gazebo
^^^^^^^^^^^^^
If you are comfortable simulating things in ``ROS`` and to put it in ``Gazebo``, :doc:`start here <./ros_to_gazebo/index>`.


:doc:`← Getting Started <./index>` 
