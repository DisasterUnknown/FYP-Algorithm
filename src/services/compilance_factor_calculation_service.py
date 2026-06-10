import math

def compilance_factor_calculation_service(domain_sorted_nodes: dict):
    domain_compliance_factor = {}
    raw_scores = {}

    for domain in domain_sorted_nodes.keys():
        nodes = domain_sorted_nodes[domain]
        if not nodes:
            raw_scores[domain] = 0.0
            continue

        regulated_operations = 0
        for node in nodes:
            regulated_operations += int(getattr(node, "contains_database_access", False))
            regulated_operations += int(getattr(node, "contains_network_access", False))
            regulated_operations += int(getattr(node, "contains_crypto_usage", False))
            regulated_operations += int(getattr(node, "contains_file_access", False))
            regulated_operations += int(getattr(node, "contains_auth_usage", False))

        max_possible = len(nodes) * 5
        if max_possible <= 0:
            raw_scores[domain] = 0.0
        else:
            raw_scores[domain] = regulated_operations / max_possible

    max_raw = max(raw_scores.values()) if raw_scores else 0.0
    if max_raw <= 0:
        return {
            domain: 0.0
            for domain in raw_scores.keys()
        }

    for domain, score in raw_scores.items():
        compressed = math.sqrt(score)
        domain_compliance_factor[domain] = round(compressed, 4)

    return domain_compliance_factor