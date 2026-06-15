import math
from config.hyperparameters import *

def quantum_risk_algorithem(
    domain_sorted_nodes,
    domain_complexity_score,
    domain_systems_score,
    domain_sensitivity_factor,
    domain_impact_score,
    domain_compliance_factor,
    project_legacy,
    project_agility
):
    domain_risk = {}
    raw_risks = []

    for domain, nodes in domain_sorted_nodes.items():
        file_risks = {}
        base_x_map = {
            "finance": 10,
            "security": 3,
            "other": 5
        }

        base_x = base_x_map.get(domain, 5)

        sensitivity = domain_sensitivity_factor.get(domain, 1.0)
        compliance = domain_compliance_factor.get(domain, 1.0)

        complexity = domain_complexity_score.get(domain, 0.0)
        systems = domain_systems_score.get(domain, {}).get("systems_count", 0)
        impact = domain_impact_score.get(domain, 1.0)

        domain_total_risk = 0.0
        for node in nodes:
            # X (file-level contribution)
            X = base_x * sensitivity * compliance

            # Y (file-level migration effort)
            fan_in = len(getattr(node, "graph_incoming_edges", []) or [])
            fan_out = len(getattr(node, "graph_outgoing_edges", []) or [])
            local_system_factor = (fan_in + fan_out) / (systems + 1)

            Y = 1 + (ALPHA * systems * complexity * local_system_factor) + project_legacy - project_agility

            # Time Risk
            Z_eff = max(1e-6, (Z - DELTA))

            time_risk = ((X + Y) / Z_eff) ** GAMMA
            time_risk = min(1.0, time_risk)

            # Exposure (file-level)
            exposure = math.log10(10 + (fan_in + fan_out))

            # File Risk
            file_risk = time_risk * (impact ** 2) * exposure

            file_name = getattr(node, "file_name", str(node))
            file_risks[file_name] = file_risk

            domain_total_risk += file_risk

        # Domain normalization
        domain_risk[domain] = {
            "raw": domain_total_risk,
            "files": file_risks
        }

        raw_risks.append(domain_total_risk)

    # Normalize domain scores (0–10)
    if not raw_risks:
        return {}

    min_r = min(raw_risks)
    max_r = max(raw_risks)

    final_scores = {}
    for domain, data in domain_risk.items():
        r = data["raw"]

        if max_r == min_r:
            normalized = 5.0
        else:
            normalized = 1 + ((r - min_r) / (max_r - min_r)) * 9

        final_scores[domain] = {
            "score": round(normalized, 4),
            "files": data["files"]
        }

    return final_scores