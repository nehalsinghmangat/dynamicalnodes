dynamicalnodes
==============

**dynamicalnodes** is a Python framework for modeling control systems as discrete-time diagrams and then deploying them as ROS2 nodes.

This website is a work in progress. Proceed at your own risk.

To get started, :doc:`install the package <installation>` and begin the :doc:`first tutorial <tutorials/0_cruise_control/0_cruise_control>`. 

.. toctree::
   :hidden:

   installation
   tutorials/index
   fh_library/index   
   api/index
   license

.. raw:: html

   <div id="dn-tabs" style="display:flex;gap:0;margin-bottom:1rem;border-bottom:2px solid #ccc;">
     <button id="tab-cruise" onclick="dnTab('cruise')"
       style="padding:0.4rem 1rem;border:none;background:none;cursor:pointer;
              font-weight:600;color:#2980b9;border-bottom:2px solid #2980b9;margin-bottom:-2px;">
       Cruise Control
     </button>

   <button id="tab-async" onclick="dnTab('async')"
       style="padding:0.4rem 1rem;border:none;background:none;cursor:pointer;
              color:#888;border-bottom:2px solid transparent;margin-bottom:-2px;">
       Async
     </button>
   </div>

     <button id="tab-changing" onclick="dnTab('changing')"
       style="padding:0.4rem 1rem;border:none;background:none;cursor:pointer;
              color:#888;border-bottom:2px solid transparent;margin-bottom:-2px;">
       Multiple Systems
     </button>   

   <div id="view-cruise">
   <div style="display:grid;grid-template-columns:auto 1fr;gap:0.75rem 1.5rem;align-items:start;margin:1.5rem 0;">

     <div style="text-align:center;">
       <img src="_static/figures/f_h.svg" style="width:3rem;" alt="f h">
     </div>
     <div>
       <img src="_static/figures/feedback_diagram_discrete_time.svg"
            style="width:100%;display:block;margin-bottom:0.75rem;" alt="Discrete-time feedback diagram">
       <img src="_static/figures/system_car.svg"
            style="width:35%;display:block;margin:0 auto;" alt="Car plant">
     </div>

     <div style="text-align:center;">
       <img src="_static/figures/logo_python.svg" style="width:3rem;" alt="Python logo">
     </div>
     <div>
       <a href="api/dynamical_system.html"><code style="display:block;margin-bottom:0.5rem;">dn.DynamicalSystem</code></a>
       <img src="_static/figures/feedback_diagram_dynamicalsystem_objects.svg"
            style="width:100%;display:block;margin-bottom:0.75rem;" alt="DynamicalSystem objects diagram">
       <img src="_static/figures/cruise_control_dynamicalsystem_plot.png"
            style="width:100%;display:block;" alt="Cruise control simulation plot">
     </div>

     <div style="text-align:center;">
       <img src="_static/figures/logo_ros.svg" style="width:5rem;" alt="ROS logo">
     </div>
     <div>
       <a href="api/rosnode.html"><code style="display:block;margin-bottom:0.5rem;">dn.ROSNode</code></a>
       <img src="_static/figures/rosgraph.svg"
            style="width:80%;display:block;margin:0 auto;" alt="ROS graph">
       <img src="_static/figures/cruise_control.gif"
            style="width:100%;display:block;" alt="Cruise control live demo">
     </div>

   </div>
   </div>

   <div id="view-async" style="display:none;">
   <div style="display:grid;grid-template-columns:auto 1fr;gap:0.75rem 1.5rem;align-items:start;margin:1.5rem 0;">
     <div style="text-align:center;">
       <img src="_static/figures/f_h.svg" style="width:3rem;" alt="f h">
     </div>
     <div>
       <img src="_static/figures/feedback_diagram_async_sensors.svg"
            style="width:100%;display:block;margin-bottom:0.75rem;" alt="Async sensor feedback diagram">
       <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;">
         <img src="_static/figures/sensor_gps.svg"
              style="width:100%;display:block;" alt="GPS">
         <img src="_static/figures/sensor_imu.svg"
              style="width:100%;display:block;margin-top:1.5rem;" alt="IMU">
       </div>
     </div>

     <div style="text-align:center;">
       <img src="_static/figures/logo_python.svg" style="width:3rem;" alt="Python logo">
     </div>
     <div>
       <a href="api/dynamical_system.html"><code style="display:block;margin-bottom:0.5rem;">dn.DynamicalSystem</code></a>
       <img src="_static/figures/sensors_gps_imu_observers.svg"
            style="width:100%;display:block;" alt="GPS/IMU observers">
     </div>

     <div style="text-align:center;">
       <img src="_static/figures/logo_ros.svg" style="width:5rem;" alt="ROS logo">
     </div>
     <div>
       <a href="api/rosnode.html"><code style="display:block;margin-bottom:0.5rem;">dn.ROSNode</code></a>
       <img src="_static/figures/rosgraph_imu_gps.svg"
            style="width:80%;display:block;margin:0 auto;" alt="ROS graph IMU GPS">
       <img src="_static/figures/gps_imu.gif"
            style="width:100%;display:block;" alt="GPS IMU live demo">
     </div>

   </div>
   </div>

   <div id="view-changing" style="display:none;">
   <div style="display:grid;grid-template-columns:auto 1fr;gap:0.75rem 1.5rem;align-items:start;margin:1.5rem 0;">

     <div style="text-align:center;">
       <img src="_static/figures/f_h.svg" style="width:3rem;" alt="f h">
     </div>
     <div>
       <img src="_static/figures/feedback_diagram_discrete_time_swap.svg"
            style="width:100%;display:block;" alt="Discrete-time swap diagram">
     </div>

     <div style="text-align:center;">
       <img src="_static/figures/logo_python.svg" style="width:3rem;" alt="Python logo">
     </div>
     <div>
       <img src="_static/figures/feedback_diagram_dynamicalsystem_swap.svg"
            style="width:100%;display:block;" alt="DynamicalSystem swap diagram">
     </div>

     <div style="text-align:center;">
       <img src="_static/figures/logo_python.svg" style="width:3rem;" alt="Python logo">
     </div>
     <div>
       <img src="_static/figures/block_dynamic_params_encaps_systems.svg"
            style="width:100%;display:block;" alt="Block dynamic params encapsulated systems">
     </div>

   </div>
   </div>

   <script>
   function dnTab(name) {
     ['cruise','async','changing'].forEach(function(v) {
       document.getElementById('view-' + v).style.display = (v === name) ? '' : 'none';
       var btn = document.getElementById('tab-' + v);
       btn.style.color        = (v === name) ? '#2980b9' : '#888';
       btn.style.borderBottom = (v === name) ? '2px solid #2980b9' : '2px solid transparent';
       btn.style.fontWeight   = (v === name) ? '600' : 'normal';
     });
   }
   </script>
