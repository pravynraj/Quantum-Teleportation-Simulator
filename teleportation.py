"""Quantum teleportation circuits and Aer execution."""

from dataclasses import dataclass

import numpy as np
from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister, transpile
from qiskit.quantum_info import DensityMatrix, Statevector
from qiskit_aer import AerSimulator

from fidelity import calculate_fidelity
from noise_model import NoiseConfig, build_noise_model


@dataclass(frozen=True)
class InputState:
    """A named, normalized single-qubit state."""

    name: str
    amplitudes: tuple[complex, complex]

    def as_statevector(self) -> Statevector:
        return Statevector(np.asarray(self.amplitudes, dtype=complex))


def make_input_state(theta: float, phi: float = 0.0, name: str = "Arbitrary") -> InputState:
    """Create cos(theta/2)|0> + exp(i*phi)sin(theta/2)|1>, in radians."""
    if not np.isfinite(theta) or not np.isfinite(phi):
        raise ValueError("theta and phi must be finite numbers.")
    return InputState(
        name=name,
        amplitudes=(
            complex(np.cos(theta / 2.0)),
            complex(np.exp(1j * phi) * np.sin(theta / 2.0)),
        ),
    )


def get_input_states(theta: float = 1.1, phi: float = 0.7) -> dict[str, InputState]:
    """Return the standard test states and one reproducible arbitrary state."""
    return {
        "|0>": InputState("|0>", (1.0 + 0j, 0j)),
        "|1>": InputState("|1>", (0j, 1.0 + 0j)),
        "|+>": InputState("|+>", (1 / np.sqrt(2), 1 / np.sqrt(2))),
        "|->": InputState("|->", (1 / np.sqrt(2), -1 / np.sqrt(2))),
        "Arbitrary": make_input_state(theta, phi),
    }


def build_teleportation_circuit(state: InputState, save_state: bool = False) -> QuantumCircuit:
    """Build the three-qubit teleportation protocol with classical feed-forward."""
    alice_input = QuantumRegister(1, "input")
    alice_pair = QuantumRegister(1, "alice")
    bob = QuantumRegister(1, "bob")
    measurements = ClassicalRegister(2, "measure")
    circuit = QuantumCircuit(alice_input, alice_pair, bob, measurements)

    # State preparation is idealized; the configured noise acts on protocol gates.
    circuit.initialize(state.as_statevector(), alice_input[0])
    circuit.h(alice_pair[0])
    circuit.cx(alice_pair[0], bob[0])
    circuit.barrier()
    circuit.cx(alice_input[0], alice_pair[0])
    circuit.h(alice_input[0])
    circuit.measure(alice_input[0], measurements[0])
    circuit.measure(alice_pair[0], measurements[1])

    with circuit.if_test((measurements[1], 1)):
        circuit.x(bob[0])
    with circuit.if_test((measurements[0], 1)):
        circuit.z(bob[0])

    if save_state:
        circuit.save_density_matrix([bob[0]], label="bob_density_matrix")
    return circuit


@dataclass(frozen=True)
class SimulationResult:
    """Single simulation output, including Bob's reduced density matrix."""

    state_name: str
    fidelity: float
    bob_density_matrix: np.ndarray
    counts: dict[str, int]
    measurement_probabilities: dict[str, float]


def simulate_teleportation(
    state: InputState,
    noise: NoiseConfig | None = None,
    shots: int = 2048,
    seed: int = 1234,
) -> SimulationResult:
    """Run teleportation on Aer and compare Bob's state with the input."""
    if shots < 1:
        raise ValueError("shots must be at least 1.")
    if seed < 0:
        raise ValueError("seed must be non-negative.")

    noise_config = noise or NoiseConfig()
    model = build_noise_model(noise_config)
    simulator = AerSimulator(method="density_matrix", noise_model=model)
    circuit = build_teleportation_circuit(state, save_state=True)
    compiled = transpile(circuit, simulator, seed_transpiler=seed)
    result = simulator.run(compiled, shots=shots, seed_simulator=seed).result()
    data = result.data(0)

    bob_density_matrix = np.asarray(data["bob_density_matrix"], dtype=complex)
    counts = {str(bits): int(count) for bits, count in data["counts"].items()}
    total = sum(counts.values())
    measurement_probabilities = {
        bits: count / total for bits, count in counts.items()
    }
    fidelity = calculate_fidelity(state.as_statevector(), DensityMatrix(bob_density_matrix))
    return SimulationResult(
        state_name=state.name,
        fidelity=fidelity,
        bob_density_matrix=bob_density_matrix,
        counts=counts,
        measurement_probabilities=measurement_probabilities,
    )
