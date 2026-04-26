dynamicalnodes: From Theory to Python to ROS
===================================
**dynamicalnodes** is a Python development framework that bridges the chasm between theoretical control systems and their implementation in hardware. Designed for hobbyists, students, and academics alike, this framework won't cure cancer, but it can do the next best thing: make controlling robots easier.

To learn more about the **dynamicalnodes** package and how to use it, see the :doc:`getting_started/index` guide in the sidebar.

To access community-made tutorial notebooks, example systems, and other fun robot things, see the :doc:`community/index` page in the sidebar. 

To access the GitHub repo, `click here <https://github.com/nehalsinghmangat/dynamicalnodes?tab=readme-ov-file>`_.

=================
Algorithm Library
=================

Browse **dynamicalnodes**'s collection of implemented control and estimation algorithms!
Each algorithm links to interactive Jupyter notebooks with working code you can download and run.
Use the filters below to search by category and implementation platform.

**Want to contribute your algorithm?** See the :doc:`community/contribution_guidelines` in the community page to add your paper and implementation to the library!

.. raw:: html

   <div class="bibliography-filters">
     <div class="filter-group">
       <label for="category-filter">Category:</label>
       <select id="category-filter" class="filter-select">
         <option value="all">All</option>
         <option value="estimation">Estimation</option>
         <option value="control">Control</option>
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
       <span class="legend-item"><span class="impl-circle impl-dynamicalnodes"></span> dynamicalnodes </span>
       <span class="legend-item"><span class="impl-circle impl-turtlebot"></span> TurtleBot</span>
       <span class="legend-item"><span class="impl-circle impl-crazyflie"></span> Crazyflie</span>
     </div>
   </div>

.. bibliography::
   :all:
   :style: plain
   :list: enumerated

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Documentation

   getting_started/index
   community/index
   license

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: API Reference

   api/index
