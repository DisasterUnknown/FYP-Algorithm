"""
Quantum Risk Algorithm

This is the main controller.

Flow:

1. Collect IBM hardware measurements
2. Calculate Hardware Progress Score
3. Adjust external Q-Day estimate (Z)
4. Calculate quantum risk


Important:

This does NOT predict Q-Day.

Z comes from external research forecasts.

The hardware score only validates whether
current quantum progress supports accelerating
or slowing that assumption.
"""


import math
from src.core.quantum_hardware_validator import extract_backend_metrics
from config.hyperparameters import Z, BACKEND

# -----------------------------
# Hardware capability calculation
# -----------------------------
def calculate_hardware_progress_score(metrics):
    qubits = metrics["qubits"]
    t2 = metrics["avg_t2_us"]
    gate_time = metrics["avg_gate_time_us"]
    gate_error = metrics["avg_gate_error"]
    readout_error = metrics["avg_readout_error"]

    # More qubits improves capability,
    # but logarithmic scaling prevents
    # huge machines dominating the score.
    qubit_factor = math.log2(
        qubits + 1
    )

    # Represents how many gate operations
    # can happen before decoherence.
    # Higher T2 = better.
    coherence_factor = (t2 / max(gate_time,0.001))

    # Fidelity factor.
    # Lower error means better capability.
    fidelity_factor = ((1 - gate_error) * (1 - readout_error))

    raw_score = (qubit_factor * coherence_factor * fidelity_factor)

    # Normalize into manageable range
    return raw_score / 100


# -----------------------------
# Adjust Z
# -----------------------------
def adjust_z(baseline_z,hardware_score):
    """
    Example:
    baseline_z = 15 years
    hardware_score = 0.5

    adjusted:
    15 / 1.5
    """

    return (baseline_z / (1 + hardware_score))

# -----------------------------
# Mosca style risk calculation
# -----------------------------
def calculate_risk(X, Y, Z, impact, exposure):
    time_risk = min(1, ((X + Y) / Z))
    risk = (time_risk * (impact ** 2) * exposure)
    return risk

# -----------------------------
# MAIN
# -----------------------------
def quantum_risk_assessment():
    # Get hardware measurements
    metrics = extract_backend_metrics(BACKEND)
    print("\nHardware Metrics")

    for k,v in metrics.items():
        print(f"{k} : {v}")

    # Convert hardware into capability score
    hps = calculate_hardware_progress_score(metrics)
    print(f"\nHardware Progress Score: {hps}")

    # External forecast value
    baseline_Z = Z
    adjusted_Z = adjust_z( baseline_Z, hps)

    print("Adjusted Z:", adjusted_Z)

    # Example application data
    X = 20   # confidentiality lifetime
    Y = 5    # migration time
    impact = 0.8
    exposure = 2

    final_risk = calculate_risk(X, Y, adjusted_Z, impact, exposure)
    print("Final Quantum Risk:", final_risk) 