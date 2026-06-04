from collections import defaultdict

def file_complexity_score(node) -> float:
    # approx to 0 -> 1

    loc = getattr(node, "lines_of_code", 0)
    funcs = len(getattr(node, "function_list", []) or [])
    classes = len(getattr(node, "class_list", []) or [])
    imports = len(getattr(node, "import_list", []) or [])

    db = 1 if getattr(node, "contains_database_access", False) else 0
    net = 1 if getattr(node, "contains_network_access", False) else 0
    crypto = 1 if getattr(node, "contains_crypto_usage", False) else 0
    file_io = 1 if getattr(node, "contains_file_access", False) else 0
    auth = 1 if getattr(node, "contains_auth_usage", False) else 0

    loc_score = min(1.0, loc / 500.0)
    func_score = min(1.0, funcs / 20.0)
    class_score = min(1.0, classes / 10.0)
    import_score = min(1.0, imports / 30.0)

    system_score = (db + net + crypto + file_io + auth) / 5.0

    return (loc_score + func_score + class_score + import_score + system_score) / 5.0


def complexity_calculation_service(domain_sorted_nodes: dict) -> dict:
    domain_raw_scores = {}

    # per domain score
    for domain in domain_sorted_nodes.keys():
        nodes = domain_sorted_nodes[domain]
        if not nodes:
            domain_raw_scores[domain] = 0.0
            continue

        total = 0.0
        count = 0
        for node in nodes:
            total += file_complexity_score(node)
            count += 1

        domain_raw_scores[domain] = total / count if count > 0 else 0.0

    # normalize (0 -> 1)
    values = list(domain_raw_scores.values())
    if not values:
        return {}

    mean_v = sum(values) / len(values)

    # avoid division instability when everything is similar
    variance = sum((x - mean_v) ** 2 for x in values) / len(values)
    std_v = variance ** 0.5

    domain_complexity_score = {}
    for domain, score in domain_raw_scores.items():
        # if no variance, return stable neutral value
        if std_v == 0:
            domain_complexity_score[domain] = 0.5
        else:
            z = (score - mean_v) / std_v

            # sigmoid squash to (0,1) without hard boundaries
            domain_complexity_score[domain] = 1 / (1 + (2.718281828 ** (-z)))

    return domain_complexity_score