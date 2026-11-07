"""Null model N1: per-neuron random circular shift (plans/engineer-b.md Step 2).

Team brief section 4: "shift each neuron's trace by its own random circular offset, 500 times;
keeps each neuron's autocorrelation, breaks co-activity. Every method reports p against N1."
Shared module: Engineer A imports it read-only for M1 and M2.
"""

from __future__ import annotations

import zlib
from typing import Iterator

import numpy as np


def rng_for(seed: int, session_id: str, purpose: str) -> np.random.Generator:
    """Seeded stream per (seed, session, purpose). Never Python hash(): it is randomised per process."""
    return np.random.default_rng([seed, zlib.crc32(session_id.encode()), zlib.crc32(purpose.encode())])


def n1_offsets(n_cells: int, n_frames: int, n_shuffles: int, rng: np.random.Generator, min_shift: int = 1) -> np.ndarray:
    """int64 (n_shuffles, n_cells), uniform on [min_shift, n_frames - min_shift]."""
    if n_frames < 2 * min_shift + 1:
        raise ValueError(f"N1 needs n_frames >= 2 * min_shift + 1; got n_frames={n_frames}, min_shift={min_shift}")
    return rng.integers(min_shift, n_frames - min_shift + 1, size=(n_shuffles, n_cells), dtype=np.int64)


def circular_shift(X: np.ndarray, offsets: np.ndarray) -> np.ndarray:
    """Row i rolled by offsets[i] (np.roll convention: out[i, t] = X[i, t - offsets[i]])."""
    B = X.shape[1]
    idx = (np.arange(B)[None, :] - offsets[:, None]) % B
    return np.take_along_axis(X, idx, axis=1)


def n1_surrogates(X: np.ndarray, n_shuffles: int, rng: np.random.Generator, min_shift: int = 1) -> Iterator[np.ndarray]:
    for offs in n1_offsets(X.shape[0], X.shape[1], n_shuffles, rng, min_shift):
        yield circular_shift(X, offs)


def n1_pvalue(observed: float, null: np.ndarray) -> float:
    """One-sided "greater": (1 + #{null >= observed}) / (1 + len(null)). Minimum 1/501 for 500 shuffles."""
    if np.isnan(observed):
        return float("nan")
    null = np.asarray(null)
    return float((1 + np.sum(null >= observed)) / (1 + null.size))
