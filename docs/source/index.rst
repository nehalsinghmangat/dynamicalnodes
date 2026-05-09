dynamicalnodes
==============

**dynamicalnodes** is a Python framework for modeling control systems and deploying them as ROS2 nodes.

It follows a four-step pipeline: **Theory → Python → ROS2 → Hardware**.

Each component (plant, controller, estimator, reference generator) is modeled as a
:class:`~dynamicalnodes.DynamicalSystem` with a state transition function ``f`` and an
observation function ``h``. Components compose naturally by passing outputs of one
system as inputs to another.

.. raw:: html

   <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:1.5rem;margin:1.5rem 0;text-align:center;">

     <div>
       <p style="font-weight:600;margin-bottom:0.5rem;">Theory</p>
       <img src="_static/figures/feedback_diagram_discrete_time.svg"
            style="width:100%;margin-bottom:0.75rem;" alt="Discrete-time feedback diagram">
       <img src="_static/figures/car.svg"
            style="width:100%;" alt="Car plant">
     </div>

     <div>
       <p style="font-weight:600;margin-bottom:0.5rem;">Python</p>
       <img src="_static/figures/feedback_diagram_dynamicalsystem_objects.svg"
            style="width:100%;margin-bottom:0.75rem;" alt="DynamicalSystem objects diagram">
       <img src="_static/figures/cruise_control_dynamicalsystem_plot.png"
            style="width:100%;" alt="Cruise control simulation plot">
     </div>

     <div>
       <p style="font-weight:600;margin-bottom:0.5rem;">ROS2</p>
       <img src="_static/figures/rosgraph.svg"
            style="width:100%;margin-bottom:0.75rem;" alt="ROS graph">
       <img src="_static/figures/cruise_control.gif"
            style="width:100%;" alt="Cruise control live demo">
     </div>

   </div>
