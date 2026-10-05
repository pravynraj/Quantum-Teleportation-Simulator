"""Configurable depolarizing and readout noise for Aer simulations."""

from dataclasses import dataclass

from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error


@dataclass(frozen=True)
class NoiseConfig:
    """Per-gate depolarizing probabilities and symmetric readout error."""

    single_qubit_error: float = 0.0
    two_qubit_error: float = 0.0
    readout_error: float = 0.0

    def __post_init__(self) -> None:
        for name, value in (
            ("single_qubit_error", self.single_qubit_error),
            ("two_qubit_error", self.two_qubit_error),
            ("readout_error", self.readout_error),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1.")
        if self.readout_error > 0.5:
            raise ValueError("readout_error must not exceed 0.5.")


def build_noise_model(config: NoiseConfig) -> NoiseModel | None:
    """Build an Aer noise model; return None when every error rate is zero."""
    if (
        config.single_qubit_error == 0.0
        and config.two_qubit_error == 0.0
        and config.readout_error == 0.0
    ):
        return None

    model = NoiseModel()
    if config.single_qubit_error:
        error = depolarizing_error(config.single_qubit_error, 1)
        model.add_all_qubit_quantum_error(error, ["id", "rz", "sx", "x"])
    if config.two_qubit_error:
        model.add_all_qubit_quantum_error(
            depolarizing_error(config.two_qubit_error, 2), ["cx"]
        )
    if config.readout_error:
        error = ReadoutError(
            [
                [1.0 - config.readout_error, config.readout_error],
                [config.readout_error, 1.0 - config.readout_error],
            ]
        )
        model.add_all_qubit_readout_error(error)
    return model
