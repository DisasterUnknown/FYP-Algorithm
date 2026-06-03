import sys
import json
from pathlib import Path
from src.services.node_create_service import node_create_service
from src.services.graph_import_map_service import graph_import_map_generation
from src.services.domain_classifier_service import classify_file_nodes

def main_entry(files_list: list[Path]):
    file_nodes = node_create_service(files_list)
    file_nodes = graph_import_map_generation(file_nodes)
    file_nodes = classify_file_nodes(file_nodes)

    print(file_nodes)


data = json.loads(sys.stdin.read())
files_list = [Path(f) for f in data["files"]]

main_entry(files_list)
