# Simulation of Quantum Teleportation Using Qiskit

A runnable Qiskit/Aer project that teleports single-qubit states from Alice to Bob, compares ideal and noisy simulations, computes state fidelity, and produces experiment data and plots. An optional Streamlit dashboard provides an interactive demo.

## Features

- Standard three-qubit teleportation circuit with Alice's Bell measurement and Bob's classically controlled corrections.
- Test inputs `|0>`, `|1>`, `|+>`, `|->`, and a configurable arbitrary pure state.
- Noiseless and noisy simulations with Qiskit Aer.
- Depolarizing gate noise and symmetric readout error.
- Uhlmann state fidelity between the intended input and Bob's reduced density matrix.
- CSV results and fidelity plots from the experiment sweep.
- Streamlit UI to explore the circuit, output density matrix, fidelity, and measurement probabilities.

## Setup

Use Python 3.10 or later. From this directory, create and activate a virtual environment, then install dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, run the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Run the experiment

```powershell
python experiments.py
```

The experiment runs all five input states at single-qubit depolarizing probabilities 0, 0.005, 0.02, and 0.05. The two-qubit error is twice the listed single-qubit error and the readout error is half. These are explicit modeling choices for a reproducible sweep, not hardware calibration data.

Generated files:

- `results/fidelity_results.csv`
- `results/fidelity_vs_noise.png`
- `results/state_comparison.png`

Change `shots` or `noise_levels` in `run_experiments()` to explore other settings.

## Run the dashboard

```powershell
streamlit run app.py
```

Select an input state, noise model, error probability, and shot count in the sidebar. Click **Run simulation** to compare noisy and noiseless fidelities.

## Run tests

```powershell
python -m pytest
```

## Circuit and modeling notes

1. Alice prepares the input state while Alice and Bob create a Bell pair.
2. Alice entangles her input with her half of the pair, applies a Hadamard, and measures both qubits.
3. Bob applies `X` when Alice's second measurement bit is 1, and `Z` when her first bit is 1.
4. Aer saves Bob's reduced density matrix after correction; fidelity is calculated from that matrix and the intended input.

State preparation is treated as ideal. The configured depolarizing noise is applied to protocol gates (`id`, `rz`, `sx`, `x`, and `cx`), and readout noise is applied independently to measured bits. Simulations are shot-based, so reported noisy fidelities are sampled estimates. Noise rates are illustrative and should not be presented as properties of a particular quantum device.

The circuit uses dynamic classical control for feed-forward, which Aer supports. The resulting circuit is a simulation model; hardware backends may impose additional constraints on dynamic circuits and supported gates.
