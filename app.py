"""Interactive Streamlit dashboard for quantum teleportation."""

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from noise_model import NoiseConfig
from teleportation import (
    build_teleportation_circuit,
    get_input_states,
    make_input_state,
    simulate_teleportation,
)


st.set_page_config(page_title="Quantum Teleportation Simulator", page_icon="⚛️")
st.title("Quantum Teleportation Simulator")
st.write(
    "Teleport a single-qubit state from Alice to Bob, then compare noiseless and "
    "noisy Aer simulations."
)

states = get_input_states()
with st.sidebar:
    st.header("Simulation settings")
    state_name = st.selectbox("Input state", list(states))
    if state_name == "Arbitrary":
        theta_degrees = st.slider("θ (degrees)", 0.0, 180.0, 63.0)
        phi_degrees = st.slider("φ (degrees)", -180.0, 180.0, 40.0)
        state = make_input_state(
            np.deg2rad(theta_degrees), np.deg2rad(phi_degrees), name="Arbitrary"
        )
    else:
        state = states[state_name]
    noise_type = st.selectbox("Noise model", ["Depolarizing + readout", "Depolarizing"])
    noise_level = st.slider("Single-qubit noise probability", 0.0, 0.1, 0.02, 0.005)
    shots = st.number_input("Shots", min_value=128, max_value=20_000, value=2048, step=128)
    run = st.button("Run simulation", type="primary")

if run:
    readout_probability = noise_level / 2 if noise_type == "Depolarizing + readout" else 0.0
    configured_noise = NoiseConfig(
        single_qubit_error=noise_level,
        two_qubit_error=min(2 * noise_level, 1.0),
        readout_error=readout_probability,
    )
    noisy_result = simulate_teleportation(
        state, configured_noise, shots=int(shots), seed=2026
    )
    noiseless_result = simulate_teleportation(
        state, NoiseConfig(), shots=int(shots), seed=2026
    )

    left, right = st.columns(2)
    left.metric("Noiseless fidelity", f"{noiseless_result.fidelity:.4f}")
    right.metric(
        "Noisy fidelity",
        f"{noisy_result.fidelity:.4f}",
        delta=f"{noisy_result.fidelity - noiseless_result.fidelity:+.4f}",
    )

    with st.expander("Teleportation circuit"):
        st.code(str(build_teleportation_circuit(state).draw(output="text")))

    state_column, chart_column = st.columns(2)
    with state_column:
        st.subheader("Bob's output density matrix")
        st.dataframe(
            np.round(noisy_result.bob_density_matrix, 4),
            use_container_width=True,
        )
        st.caption(f"Input state: {state.name}")
    with chart_column:
        st.subheader("Alice's Bell-measurement outcomes")
        figure, axis = plt.subplots()
        outcomes = ["00", "01", "10", "11"]
        probabilities = [
            noisy_result.measurement_probabilities.get(outcome, 0.0)
            for outcome in outcomes
        ]
        axis.bar(outcomes, probabilities, color="#5276a7")
        axis.set(xlabel="Classical measurement bits", ylabel="Probability", ylim=(0, 1))
        st.pyplot(figure)
        plt.close(figure)
else:
    st.info("Choose an input state and noise level in the sidebar, then run the simulation.")
