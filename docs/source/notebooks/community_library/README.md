# Community Library

This directory contains community-contributed notebooks, implementations, and experiments.

## Contributing

To add your notebook to the community library:

1. Place your notebook(s) in this directory
2. Add an entry to `docs/source/community_references.bib` with:
   - Unique citation key
   - Title of your notebook
   - Your name as author
   - Year
   - Keywords (estimation, control, or other)
   - Implementation paths (impl_dynamicalnodes, impl_turtlebot, impl_crazyflie as applicable)
   - Brief note describing what your notebook does

3. Run `python3 docs/generate_bib_metadata.py` to regenerate metadata
4. Submit a pull request

See `docs/source/community/contribution_guidelines.rst` for detailed instructions.

## Naming Convention

Use descriptive names for your notebooks:
- `algorithm_name_platform.ipynb` (e.g., `adaptive_mpc_turtlebot.ipynb`)
- `topic_description_platform.ipynb` (e.g., `formation_control_crazyflie.ipynb`)
