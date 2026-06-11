import math

def project_legacy_calculation_service(file_nodes):
    if not file_nodes:
        return 0.0

    total_files = len(file_nodes)
    complexity_total = 0.0
    coupling_total = 0.0
    capability_files = 0

    all_domains = set()
    capability_domains = set()
    for node in file_nodes:
        loc = getattr(node, "lines_of_code", 0)
        funcs = len(getattr(node, "function_list", []) or [])
        classes = len(getattr(node, "class_list", []) or [])
        imports = len(getattr(node, "import_list", []) or [])

        loc_score = min(1.0, loc / 500.0)
        func_score = min(1.0, funcs / 20.0)
        class_score = min(1.0, classes / 10.0)
        import_score = min(1.0, imports / 30.0)

        file_complexity = (
            loc_score +
            func_score +
            class_score +
            import_score
        ) / 4.0

        complexity_total += file_complexity

        fan_in = len(getattr(node, "graph_incoming_edges", []) or [])
        fan_out = len(getattr(node, "graph_outgoing_edges", []) or [])

        file_coupling = math.log1p(fan_in + fan_out)
        coupling_total += file_coupling

        has_capability = (
            getattr(node, "contains_database_access", False) or
            getattr(node, "contains_network_access", False) or
            getattr(node, "contains_crypto_usage", False) or
            getattr(node, "contains_file_access", False) or
            getattr(node, "contains_auth_usage", False)
        )

        domains = getattr(node, "candidate_domains", []) or []
        all_domains.update(domains)

        if has_capability:
            capability_files += 1
            capability_domains.update(domains)

    avg_complexity = complexity_total / total_files
    avg_coupling = coupling_total / total_files
    coupling_score = min(1.0, avg_coupling / math.log1p(100))
    capability_dispersion = capability_files / total_files

    if all_domains:
        domain_fragmentation = (len(capability_domains) / len(all_domains))
    else:
        domain_fragmentation = 0.0

    legacy_score = (
        avg_complexity +
        coupling_score +
        capability_dispersion +
        domain_fragmentation
    ) / 4.0

    return round(legacy_score, 4)