================
Algorithm Library
================

Browse dynamicalnodes's collection of implemented control and estimation algorithms.
Each algorithm links to interactive Jupyter notebooks with working code you can download and run.
Use the filters below to search by category, algorithm type, and implementation platform.

.. raw:: html

   <div class="bibliography-filters">
     <div class="filter-group">
       <label for="category-filter">Category:</label>
       <select id="category-filter" class="filter-select">
         <option value="all">All</option>
         <option value="state-estimation">State Estimation</option>
         <option value="control">Control</option>
         <option value="planning">Planning</option>
         <option value="filtering">Filtering</option>
       </select>
     </div>

     <div class="filter-group">
       <label for="algorithm-filter">Algorithm:</label>
       <select id="algorithm-filter" class="filter-select">
         <option value="all">All</option>
         <option value="kalman-filter">Kalman Filter</option>
         <option value="square-root-kf">Square Root KF</option>
         <option value="partial-update-kf">Partial Update KF</option>
         <option value="ukf">Unscented Kalman Filter</option>
         <option value="particle-filter">Particle Filter</option>
         <option value="observer">Luenberger Observer</option>
         <option value="mhe">Moving Horizon Estimation</option>
         <option value="pid">PID Controller</option>
         <option value="lqr">LQR</option>
         <option value="mpc">MPC</option>
         <option value="h-infinity">H-infinity Control</option>
         <option value="sliding-mode">Sliding Mode Control</option>
       </select>
     </div>

     <div class="filter-group filter-group-vertical">
       <label class="filter-label-main">Implementation Status:</label>
       <div class="checkbox-group">
         <label class="checkbox-label">
           <input type="checkbox" class="impl-checkbox" value="dynamicalnodes">
           <span class="impl-circle impl-dynamicalnodes"></span>
           <span class="checkbox-text">dynamicalnodes</span>
         </label>
         <label class="checkbox-label">
           <input type="checkbox" class="impl-checkbox" value="turtlebot">
           <span class="impl-circle impl-turtlebot"></span>
           <span class="checkbox-text">TurtleBot</span>
         </label>
         <label class="checkbox-label">
           <input type="checkbox" class="impl-checkbox" value="crazyflie">
           <span class="impl-circle impl-crazyflie"></span>
           <span class="checkbox-text">Crazyflie</span>
         </label>
       </div>
     </div>

     <button id="reset-filters" class="reset-button">Reset Filters</button>
   </div>

   <div id="no-results-message" style="display: none; padding: 20px; background: #f8f8f8; border-radius: 4px; margin: 20px 0;">
     <strong>No papers match the selected filters.</strong> Try adjusting your filter selections.
   </div>

   <div class="legend-box">
     <strong>Legend:</strong> Click on a colored circle to view the implementation notebook.
     <div class="legend-items">
       <span class="legend-item"><span class="impl-circle impl-dynamicalnodes"></span> dynamicalnodes</span>
       <span class="legend-item"><span class="impl-circle impl-turtlebot"></span> TurtleBot</span>
       <span class="legend-item"><span class="impl-circle impl-crazyflie"></span> Crazyflie</span>
     </div>
   </div>

References
==========

.. bibliography::
   :all:
   :style: plain
   :list: enumerated
