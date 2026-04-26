=========
Community
=========

Thank you for your interest in contributing to **dynamicalnodes**! This is an open-source project by and for researchers to assist in the world of academic robotics. This page assumes you have a working knowledge of the **dynamicalnodes** package. If not, or if you'd like a refresher, please check out our :doc:`../getting_started/index` guide in the sidebar.

==================
Community Library
==================

Browse community-contributed notebooks, implementations, and experiments!
Each entry links to Jupyter notebooks shared by the community. Use the filters below to search by category and implementation platform.

**Want to contribute your notebook?** See the :doc:`contribution_guidelines` to add your implementation to the library!

.. raw:: html

   <div class="bibliography-filters">
     <div class="filter-group">
       <label for="category-filter-community">Category:</label>
       <select id="category-filter-community" class="filter-select">
         <option value="all">All</option>
         <option value="estimation">Estimation</option>
         <option value="control">Control</option>
         <option value="other">Other</option>
       </select>
     </div>

     <div class="filter-group filter-group-vertical">
       <label class="filter-label-main">Implementation Status:</label>
       <div class="checkbox-group">
         <label class="checkbox-label">
           <input type="checkbox" class="impl-checkbox-community" value="dynamicalnodes">
           <span class="impl-circle impl-dynamicalnodes"></span>
           <span class="checkbox-text">dynamicalnodes</span>
         </label>
         <label class="checkbox-label">
           <input type="checkbox" class="impl-checkbox-community" value="turtlebot">
           <span class="impl-circle impl-turtlebot"></span>
           <span class="checkbox-text">TurtleBot</span>
         </label>
         <label class="checkbox-label">
           <input type="checkbox" class="impl-checkbox-community" value="crazyflie">
           <span class="impl-circle impl-crazyflie"></span>
           <span class="checkbox-text">Crazyflie</span>
         </label>
       </div>
     </div>

     <button id="reset-filters-community" class="reset-button">Reset Filters</button>
   </div>

   <div id="no-results-message-community" style="display: none; padding: 20px; background: #f8f8f8; border-radius: 4px; margin: 20px 0;">
     <strong>No contributions match the selected filters.</strong> Try adjusting your filter selections.
   </div>

   <div class="legend-box">
     <strong>Legend:</strong> Click on a colored circle to view the implementation notebook.
     <div class="legend-items">
       <span class="legend-item"><span class="impl-circle impl-dynamicalnodes"></span> dynamicalnodes </span>
       <span class="legend-item"><span class="impl-circle impl-turtlebot"></span> TurtleBot</span>
       <span class="legend-item"><span class="impl-circle impl-crazyflie"></span> Crazyflie</span>
     </div>
   </div>

.. bibliography:: ../community_references.bib
   :all:
   :style: plain
   :list: enumerated

.. raw:: html

   <script>
   document.addEventListener('DOMContentLoaded', function() {
     // Community library filtering logic
     const categoryFilter = document.getElementById('category-filter-community');
     const implCheckboxes = document.querySelectorAll('.impl-checkbox-community');
     const resetButton = document.getElementById('reset-filters-community');
     const noResultsMsg = document.getElementById('no-results-message-community');

     // Get all bibliography entries
     const bibEntries = document.querySelectorAll('.citation-list .citation');

     function filterEntries() {
       const selectedCategory = categoryFilter.value;
       const selectedImpls = Array.from(implCheckboxes)
         .filter(cb => cb.checked)
         .map(cb => cb.value);

       let visibleCount = 0;

       bibEntries.forEach(entry => {
         let show = true;

         // Category filter
         if (selectedCategory !== 'all') {
           const hasCategory = entry.classList.contains(`category-${selectedCategory}`);
           if (!hasCategory) show = false;
         }

         // Implementation filter
         if (selectedImpls.length > 0) {
           const hasAnyImpl = selectedImpls.some(impl =>
             entry.classList.contains(`impl-${impl}`)
           );
           if (!hasAnyImpl) show = false;
         }

         entry.style.display = show ? '' : 'none';
         if (show) visibleCount++;
       });

       // Show/hide no results message
       noResultsMsg.style.display = visibleCount === 0 ? 'block' : 'none';
     }

     // Event listeners
     categoryFilter.addEventListener('change', filterEntries);
     implCheckboxes.forEach(cb => cb.addEventListener('change', filterEntries));

     resetButton.addEventListener('click', function() {
       categoryFilter.value = 'all';
       implCheckboxes.forEach(cb => cb.checked = false);
       filterEntries();
     });
   });
   </script>



