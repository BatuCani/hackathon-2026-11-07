"""Loader for the RIKEN Zenodo 17667863 ``sleep_data.mat`` (owner: Engineer A).

Builds a :class:`toolbox.contract.Recording` per split (A and B, see PROBLEM.md):
``deconv`` from ``spike``, ``sleep_stage`` from ``state.state``, ``fs = 7.65`` Hz,
``epoch`` (PRE / TASK / POST / none) from the split definitions. A missing required
field stops with a clear message. Never commits or copies the data.
"""
