import math
from collections import defaultdict

def impact_calculation_service(domain_sorted_nodes: dict):
    domain_file_impacts = {}
    domain_impact_scores = {}
    all_fan_in_values = []

    # compute fan-in values globally (needed for normalization stability)
    for domains in domain_sorted_nodes.values():
        for node in domains:
            fan_out = len(getattr(node, "graph_outgoing_edges", []) or [])
            all_fan_in_values.append(fan_out)

    max_fan_in = max(all_fan_in_values) if all_fan_in_values else 1

    # compute per-file impact
    for domain, nodes in domain_sorted_nodes.items():
        file_impacts = []
        for node in nodes:
            fan_in = len(getattr(node, "graph_incoming_edges", []) or [])
            fan_out = len(getattr(node, "graph_outgoing_edges", []) or [])

            # direct impact (log scaled)
            di = math.log1p(fan_in)
            ndi = di / math.log1p(max_fan_in) if max_fan_in > 0 else 0.0

            # structural balance factor
            cluster_factor = fan_out / (fan_in + fan_out + 1)

            # final file impact
            impact = (0.7 * ndi) + (0.3 * cluster_factor)

            file_impacts.append(impact)

        domain_file_impacts[domain] = file_impacts

    # domain aggregation
    raw_domain = {}
    for domain, impacts in domain_file_impacts.items():
        if not impacts:
            raw_domain[domain] = 0.0
        else:
            raw_domain[domain] = sum(impacts) / len(impacts)

    # stable normalization (prevents 1-domain = 1.0 issue)
    values = list(raw_domain.values())
    if not values:
        return {}

    min_v = min(values)
    max_v = max(values)

    # avoid boundary collapse 
    epsilon = 1e-9
    for domain, val in raw_domain.items():
        if max_v - min_v < epsilon:
            domain_impact_scores[domain] = 0.5      # keep neutral mid value
        else:
            normalized = (val - min_v) / (max_v - min_v)
            domain_impact_scores[domain] = max(0.05, min(0.95, normalized))     # soft clamp 

    return domain_impact_scores