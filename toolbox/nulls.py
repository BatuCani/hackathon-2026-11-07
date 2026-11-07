"""Null model N1 (owner: Engineer B).

Per-neuron circular shift, 500 shuffles: offsets, shift, one-sided p-value
(1 + #null >= observed) / (1 + n), and seeded random streams per
(seed, session_id, purpose). See plans/engineer-b.md step 2. Shifts never cross
a recording segment boundary.
"""
