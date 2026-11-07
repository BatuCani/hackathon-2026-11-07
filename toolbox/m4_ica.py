"""M4 ICA reactivation strength (team-brief ID; SoT M6 with M5). plans/engineer-b.md Step 4.

"ICA is performed on the data projected onto the subspace of the significant components ...
to de-mix the PCs into independent components" (SoT M6); IC projectors replace PC projectors.
Needs at least two significant components [brief].
"""

from __future__ import annotations

import warnings
from dataclasses import asdict, dataclass

import numpy as np
from sklearn.decomposition import FastICA
from sklearn.exceptions import ConvergenceWarning

from .assemblies import AssemblyParams, Subspace, run_assembly_method, significant_subspace
from .contract import MethodResult, Recording, Requirement
from .nulls import rng_for

METHOD_ID = "M4"


@dataclass(frozen=True)
class ICAParams:
    fun: str = "logcosh"  # all [TEAM DECISION], SoT gap 3
    whiten: str = "unit-variance"
    max_iter: int = 1000
    tol: float = 1e-4


class ICANotConverged(RuntimeError):
    pass


def _fit(Y: np.ndarray, n: int, params: ICAParams, max_iter: int, random_state: int) -> np.ndarray:
    with warnings.catch_warnings():
        warnings.simplefilter("error", ConvergenceWarning)
        ica = FastICA(n_components=n, fun=params.fun, whiten=params.whiten,
                      max_iter=max_iter, tol=params.tol, random_state=random_state)
        ica.fit(Y.T)
    return ica.components_


def ica_weights(sub: Subspace, params: ICAParams, rng: np.random.Generator) -> np.ndarray:
    """(N, n_sig) unit columns; sign so the largest-|w| entry is positive.

    Y = V_sig^T Z_TASK; FastICA on Y^T; W = V_sig @ components_.T.
    ConvergenceWarning: retry once with max_iter 5000, then raise ICANotConverged.
    """
    Y = sub.V_sig.T @ sub.Z["TASK"]
    random_state = int(rng.integers(0, 2**31 - 1))
    try:
        comps = _fit(Y, sub.n_sig, params, params.max_iter, random_state)
    except ConvergenceWarning:
        try:
            comps = _fit(Y, sub.n_sig, params, 5000, random_state)
        except ConvergenceWarning as e:
            raise ICANotConverged("ICA did not converge") from e
    W = sub.V_sig @ comps.T
    W /= np.linalg.norm(W, axis=0, keepdims=True)
    signs = np.sign(W[np.argmax(np.abs(W), axis=0), np.arange(W.shape[1])])
    return W * np.where(signs == 0, 1.0, signs)


def check_requirements(rec: Recording, params: AssemblyParams | None = None, seed: int = 0) -> Requirement:
    params = params or AssemblyParams()
    sub = significant_subspace(rec, params, seed)
    if isinstance(sub, Requirement):
        return sub
    if sub.n_sig < 2:
        return Requirement(False, f"{sub.n_sig} < 2 significant components",
                           ("at least 2 TASK components above the N1 eigenvalue bound",))
    return Requirement(True, "", ())


def run_with_traces(rec: Recording, *, seed: int, params: AssemblyParams | None = None, ica: ICAParams | None = None):
    ica = ica or ICAParams()

    def weights(sub: Subspace):
        try:
            return ica_weights(sub, ica, rng_for(seed, rec.session_id, "ica"))
        except ICANotConverged:
            return Requirement(False, "ICA did not converge", ("ICA convergence (max_iter 5000)",))

    return run_assembly_method(
        rec, method_id=METHOD_ID, seed=seed, params=params or AssemblyParams(), min_sig=2,
        weights=weights, extra_params={"ica": asdict(ica)},
    )


def run(rec: Recording, *, seed: int, params: AssemblyParams | None = None, ica: ICAParams | None = None) -> MethodResult:
    return run_with_traces(rec, seed=seed, params=params, ica=ica)[0]
