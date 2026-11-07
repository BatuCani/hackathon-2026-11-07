"""M3 PCA reactivation strength (owner: Engineer B).

Key D3 = mean over significant TASK components of mean R_k(POST) - mean R_k(PRE).
Needs at least one TASK component above the N1 eigenvalue bound.
Exposes ``check_requirements(rec, params)`` and ``run(rec, *, seed, params=None)``
returning :class:`toolbox.contract.MethodResult`.
"""
