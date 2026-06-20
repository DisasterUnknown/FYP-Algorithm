"""
Quantum Hardware Validator

Collects IBM backend calibration metrics.

Handles missing calibration values because
real quantum devices may not have complete
measurements for every qubit.
"""

from qiskit_ibm_runtime import QiskitRuntimeService



def extract_backend_metrics(backend_name):
    service = QiskitRuntimeService(channel="ibm_quantum_platform")
    backend = service.backend(backend_name)
    properties = backend.properties()
    qubit_count = backend.num_qubits

    t1_values = []
    t2_values = []
    readout_errors = []

    for q in range(qubit_count):
        # T1
        try:
            t1 = properties.t1(q)
            if t1:
                t1_values.append(t1 * 1_000_000)

        except Exception:
            pass

        # T2
        #
        # Some IBM qubits may not have
        # calibration data available.
        try:
            t2 = properties.t2(q)
            if t2:
                t2_values.append(t2 * 1_000_000)

        except Exception:
            pass

        # Readout error
        try:
            readout = properties.readout_error(q)
            if readout:
                readout_errors.append(readout)

        except Exception:
            pass

    gate_errors = []
    gate_times = []
    for gate in properties.gates:
        if gate.gate in ["cx", "ecr", "cz"]:
            for parameter in gate.parameters:
                if parameter.name == "gate_error":
                    gate_errors.append(parameter.value)

                if parameter.name == "gate_length":
                    gate_times.append(parameter.value)

    metrics = {
        "qubits": qubit_count,
        "avg_t1_us": sum(t1_values) / max(len(t1_values),1),
        "avg_t2_us": sum(t2_values) / max(len(t2_values),1),
        "avg_gate_error": sum(gate_errors) / max(len(gate_errors),1),
        "avg_gate_time_us": sum(gate_times) / max(len(gate_times),1),
        "avg_readout_error": sum(readout_errors) / max(len(readout_errors),1)
    }

    return metrics