"""M3 PCA reactivation strength (team-brief ID; SoT M4 with M5). plans/engineer-b.md Step 3.

"Yes" direction: mean strength in POST > PRE [brief]; needs at least one significant TASK component.
"""

from __future__ import annotations

from .assemblies import AssemblyParams, run_assembly_method
from .contract import MethodResult, Recording, Requirement
from .assemblies import significant_subspace

METHOD_ID = "M3"


def check_requirements(rec: Recording, params: AssemblyParams | None = None, seed: int = 0) -> Requirement:
    """Runs the N1 eigenvalue bound, because n_sig needs it (plan section 6)."""
    params = params or AssemblyParams()
    sub = significant_subspace(rec, params, seed)
    if isinstance(sub, Requirement):
        return sub
    if sub.n_sig < 1:
        return Requirement(False, "0 TASK components above N1 bound", ("at least 1 TASK component above the N1 eigenvalue bound",))
    return Requirement(True, "", ())


def run_with_traces(rec: Recording, *, seed: int, params: AssemblyParams | None = None):
    return run_assembly_method(
        rec, method_id=METHOD_ID, seed=seed, params=params or AssemblyParams(), min_sig=1,
        weights=lambda sub: sub.V_sig,
    )


def run(rec: Recording, *, seed: int, params: AssemblyParams | None = None) -> MethodResult:
    return run_with_traces(rec, seed=seed, params=params)[0]
