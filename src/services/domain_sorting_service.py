import config.domain_list
from collections import defaultdict

def domain_sorting(file_nodes):
    domain_list = {d.lower() for d in config.domain_list.DOMAIN_LIST}
    domain_sorted_nodes = defaultdict(list)

    for node in file_nodes:
        domains = node.candidate_domains.keys()

        if not domains:
            domain_sorted_nodes["other"].append(node)
            continue

        matched = False
        for domain in domains:
            domain = domain.lower()

            if domain in domain_list:
                domain_sorted_nodes[domain].append(node)
                matched = True

        if not matched:
            domain_sorted_nodes["other"].append(node)

    return dict(domain_sorted_nodes)