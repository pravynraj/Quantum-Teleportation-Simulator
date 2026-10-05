"""State fidelity helpers for single-qubit teleportation results."""

import numpy as np
from qiskit.quantum_info import DensityMatrix, Statevector, state_fidelity


def calculate_fidelity(
    expected_state: Statevector | DensityMatrix | np.ndarray,
    actual_state: DensityMatrix | np.ndarray,
) -> float:
    """Return the Uhlmann fidelity between two quantum states."""
    expected = (
        expected_state
        if isinstance(expected_state, (Statevector, DensityMatrix))
        else DensityMatrix(expected_state)
    )
    actual = (
        actual_state
        if isinstance(actual_state, (Statevector, DensityMatrix))
        else DensityMatrix(actual_state)
    )
    return float(state_fidelity(expected, actual))
