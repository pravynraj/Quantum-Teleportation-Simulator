"""Run the state/noise sweep and save its CSV and plots."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from noise_model import NoiseConfig
from teleportation import get_input_states, simulate_teleportation


DEFAULT_NOISE_LEVELS = (0.0, 0.005, 0.02, 0.05)
RESULTS_DIR = Path(__file__).resolve().parent / "results"


def run_experiments(
    output_dir: Path = RESULTS_DIR,
    shots: int = 2048,
    noise_levels: tuple[float, ...] = DEFAULT_NOISE_LEVELS,
) -> pd.DataFrame:
    """Simulate each standard state at every noise level and save outputs."""
    if not noise_levels or any(not 0.0 <= level <= 1.0 for level in noise_levels):
        raise ValueError("noise_levels must be a non-empty sequence between 0 and 1.")
    output_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, float | int | str]] = []
    states = get_input_states()

    for state_index, state in enumerate(states.values()):
        for level_index, level in enumerate(noise_levels):
            result = simulate_teleportation(
                state,
                NoiseConfig(
                    single_qubit_error=level,
                    two_qubit_error=min(2.0 * level, 1.0),
                    readout_error=min(level / 2.0, 0.5),
                ),
                shots=shots,
                seed=1234 + state_index * len(noise_levels) + level_index,
            )
            rows.append(
                {
                    "state": state.name,
                    "single_qubit_error": level,
                    "two_qubit_error": min(2.0 * level, 1.0),
                    "readout_error": min(level / 2.0, 0.5),
                    "shots": shots,
                    "fidelity": result.fidelity,
                }
            )

    frame = pd.DataFrame(rows)
    frame.to_csv(output_dir / "fidelity_results.csv", index=False)
    _plot_fidelity_vs_noise(frame, output_dir / "fidelity_vs_noise.png")
    _plot_state_comparison(frame, output_dir / "state_comparison.png")
    return frame


def _plot_fidelity_vs_noise(frame: pd.DataFrame, path: Path) -> None:
    figure, axis = plt.subplots(figsize=(8, 5))
    for state_name, group in frame.groupby("state", sort=False):
        axis.plot(
            group["single_qubit_error"],
            group["fidelity"],
            marker="o",
            label=state_name,
        )
    axis.set(
        title="Teleportation fidelity vs. depolarizing noise",
        xlabel="Single-qubit depolarizing probability",
        ylabel="State fidelity",
        ylim=(0.0, 1.05),
    )
    axis.grid(alpha=0.3)
    axis.legend(title="Input state")
    figure.tight_layout()
    figure.savefig(path, dpi=160)
    plt.close(figure)


def _plot_state_comparison(frame: pd.DataFrame, path: Path) -> None:
    pivot = frame.pivot(
        index="state", columns="single_qubit_error", values="fidelity"
    )
    axis = pivot.plot(kind="bar", figsize=(9, 5), ylim=(0.0, 1.05))
    axis.set(
        title="Teleportation fidelity by input state and noise level",
        xlabel="Input state",
        ylabel="State fidelity",
    )
    axis.grid(axis="y", alpha=0.3)
    axis.legend(title="Single-qubit error")
    axis.figure.tight_layout()
    axis.figure.savefig(path, dpi=160)
    plt.close(axis.figure)


if __name__ == "__main__":
    results = run_experiments()
    print(results.to_string(index=False))
    print(f"\nSaved CSV and plots in: {RESULTS_DIR}")
