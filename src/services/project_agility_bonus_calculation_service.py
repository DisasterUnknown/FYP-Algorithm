import math

def project_agility_bonus_calculation(file_nodes):
    if not file_nodes:
        return 0.0

    total_dependency_score = 0.0
    total_complexity_score = 0.0
    total_capability_score = 0.0

    capability_files = 0
    for node in file_nodes:
        fan_in = len(getattr(node, "graph_incoming_edges", []) or [])
        fan_out = len(getattr(node, "graph_outgoing_edges", []) or [])

        dependency_count = fan_in + fan_out
        dependency_score = 1.0 - min(
            1.0,
            math.log1p(dependency_count) / math.log1p(50)
        )

        loc = getattr(node, "lines_of_code", 0)
        funcs = len(getattr(node, "function_list", []) or [])
        classes = len(getattr(node, "class_list", []) or [])

        loc_score = min(1.0, loc / 500.0)
        func_score = min(1.0, funcs / 20.0)
        class_score = min(1.0, classes / 10.0)

        complexity_score = (
            loc_score +
            func_score +
            class_score
        ) / 3.0

        simplicity_score = 1.0 - complexity_score

        has_capability = (
            getattr(node, "contains_database_access", False)
            or getattr(node, "contains_network_access", False)
            or getattr(node, "contains_crypto_usage", False)
            or getattr(node, "contains_file_access", False)
            or getattr(node, "contains_auth_usage", False)
        )

        if has_capability:
            capability_files += 1

        total_dependency_score += dependency_score
        total_complexity_score += simplicity_score
        total_capability_score += int(has_capability)

    file_count = len(file_nodes)

    avg_dependency_score = total_dependency_score / file_count
    avg_simplicity_score = total_complexity_score / file_count

    capability_concentration = 1.0 - (
        capability_files / file_count
    )

    agility_bonus = (
        (0.40 * avg_dependency_score) +
        (0.35 * avg_simplicity_score) +
        (0.25 * capability_concentration)
    )

    return round(
        max(0.0, min(1.0, agility_bonus)),
        4
    )