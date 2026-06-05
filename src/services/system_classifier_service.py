from collections import defaultdict
from math import log1p

def systems_calculation_service(domain_sorted_nodes: dict) -> dict:
    domain_systems_score = {}
    domain_systems_count = {}

    for domain, nodes in domain_sorted_nodes.items():
        if not nodes:
            domain_systems_score[domain] = 0.0
            domain_systems_count[domain] = 0.0
            continue

        # structural component (bounded per domain)
        file_count = len(nodes)

        # graph connectivity inside domain
        node_ids = {node.file_path: i for i, node in enumerate(nodes)}
        adj = defaultdict(set)

        for node in nodes:
            src = node_ids[node.file_path]
            for e in getattr(node, "graph_outgoing_edges", []) or []:
                if e in node_ids:
                    adj[src].add(node_ids[e])
            for e in getattr(node, "graph_incoming_edges", []) or []:
                if e in node_ids:
                    adj[node_ids[e]].add(src)

        visited = set()
        components = 0
        for i in range(len(nodes)):
            if i in visited:
                continue

            stack = [i]
            components += 1
            while stack:
                n = stack.pop()
                if n in visited:
                    continue
                visited.add(n)

                for nxt in adj[n]:
                    if nxt not in visited:
                        stack.append(nxt)

        structural_score = min(1.0, components / max(1, file_count))

        # capability diversity (bounded)
        caps = set()
        for node in nodes:
            if getattr(node, "contains_database_access", False):
                caps.add("db")
            if getattr(node, "contains_network_access", False):
                caps.add("net")
            if getattr(node, "contains_crypto_usage", False):
                caps.add("crypto")
            if getattr(node, "contains_file_access", False):
                caps.add("file_io")
            if getattr(node, "contains_auth_usage", False):
                caps.add("auth")

        capability_score = len(caps) / 5.0

        # external coupling (bounded, log-scaled)
        external_edges = set()
        for node in nodes:
            for e in getattr(node, "graph_outgoing_edges", []) or []:
                if e not in node_ids:
                    external_edges.add(e)
            for e in getattr(node, "graph_incoming_edges", []) or []:
                if e not in node_ids:
                    external_edges.add(e)

        external_score = min(1.0, log1p(len(external_edges)) / 10.0)

        # final systems score (NO explosion, NO sigmoid)
        systems_score = (
            structural_score +
            capability_score +
            external_score
        ) / 3.0

        # interpretable systems count (soft, not raw sum)
        systems_count = (
            components +
            len(caps) +
            min(5, len(external_edges) / 3.0)
        )

        domain_systems_score[domain] = round(systems_score, 4)
        domain_systems_count[domain] = round(systems_count, 2)

    return {
        "systems_score": domain_systems_score,
        "systems_count": domain_systems_count
    }