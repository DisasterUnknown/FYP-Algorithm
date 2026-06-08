import math

def sensitivity_factor_calculation_service(domain_sorted_nodes: dict):
    domain_sensitivity_factor = {}

    file_scores = []
    for domain in domain_sorted_nodes.keys():
        nodes = domain_sorted_nodes[domain]

        if not nodes:
            domain_sensitivity_factor[domain] = 0.0
            continue

        domain_file_scores = []
        for node in nodes:
            fan_in = len(getattr(node, "graph_incoming_edges", []) or [])
            fan_out = len(getattr(node, "graph_outgoing_edges", []) or [])

            degree = fan_in + fan_out

            capability_count = 0
            capability_count += int(getattr(node, "contains_database_access", False))
            capability_count += int(getattr(node, "contains_network_access", False))
            capability_count += int(getattr(node, "contains_crypto_usage", False))
            capability_count += int(getattr(node, "contains_file_access", False))
            capability_count += int(getattr(node, "contains_auth_usage", False))

            fan_in_score = min(1.0, math.log1p(fan_in) / math.log1p(50))
            degree_score = min(1.0, math.log1p(degree) / math.log1p(100))
            capability_score = capability_count / 5.0

            file_sensitivity = (
                (0.20 * fan_in_score) +
                (0.10 * degree_score) +
                (0.70 * capability_score)
            )

            domain_file_scores.append(file_sensitivity)
            file_scores.append(file_sensitivity)

        max_score = max(domain_file_scores)
        avg_score = sum(domain_file_scores) / len(domain_file_scores)

        domain_sensitivity_factor[domain] = (
            (0.7 * max_score) +
            (0.3 * avg_score)
        )

    if not file_scores:
        return {}

    max_possible = max(file_scores)
    if max_possible <= 0:
        return {
            domain: 0.0
            for domain in domain_sensitivity_factor.keys()
        }

    for domain in domain_sensitivity_factor.keys():
        domain_sensitivity_factor[domain] = round(
            domain_sensitivity_factor[domain] / max_possible,
            4
        )

    return domain_sensitivity_factor