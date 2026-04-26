:doc:`← Theory to Python <index>`

======================================
 Control Systems as Dynamical Systems
======================================

    "All the world is a [dynamical system], and all the men and women merely [dynamical systems]."

    -- Shakespeare (paraphrased)
    
This section consists of three examples of using the ``dynamicalnodes.DynamicalSystem`` and ``dynamicalnodes.DataChange`` modules to model and simulate control systems.

"Example: Car Cruise Control" walks the reader through modeling a classic feedback system as the composition of dynamical systems. We recommended starting here.

"Example: Turtlebot with Noisy Odometry" walks the reader through modeling a simple ``ROS`` robot with realistic noisy data. 

"Example: Crazyflie Multi-Sensor Fusion" walks the reader through a more sophisticated ``ROS`` robot that integrates noisy and asynchronous data from multiple sources.  

..  toctree::
    :caption: Core Examples
    :maxdepth: 2

    ../../notebooks/tutorial/theory_to_python/car_cruise_control
    ../../notebooks/tutorial/theory_to_python/turtlebot_state_estimation
    ../../notebooks/tutorial/theory_to_python/crazyflie_sensor_fusion

:doc:`← Theory to Python <index>`
