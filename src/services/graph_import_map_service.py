def graph_import_map_generation(file_nodes):
    # build fast lookup: file_path -> node
    node_map = {node.file_path: node for node in file_nodes}

    # resolve edges in one pass
    for node in file_nodes:
        for incoming_path in node.graph_incoming_edges:
            target_node = node_map.get(incoming_path)
            if target_node:
                target_node.graph_outgoing_edges.append(node.file_path)

    return file_nodes