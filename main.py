import sys
import json
from pathlib import Path
from src.services.node_create_service import node_create_service
from src.services.graph_import_map_service import graph_import_map_generation
from src.services.domain_classifier_service import classify_file_nodes
from src.services.domain_sorting_service import domain_sorting
from src.services.complexity_calculation_service import complexity_calculation_service
from src.services.system_classifier_service import systems_calculation_service
from src.services.sensitivity_factor_calculation_service import sensitivity_factor_calculation_service
from src.services.impact_calculation_service import impact_calculation_service
from src.services.compilance_factor_calculation_service import compilance_factor_calculation_service
from src.services.project_legacy_calculation_service import project_legacy_calculation_service

def main_entry(files_list: list[Path]):
    file_nodes = node_create_service(files_list)
    file_nodes = graph_import_map_generation(file_nodes)
    file_nodes = classify_file_nodes(file_nodes)

    project_legacy_value = project_legacy_calculation_service(file_nodes)

    domain_sorted_nodes = domain_sorting(file_nodes)
    domain_complexity_score = complexity_calculation_service(domain_sorted_nodes)
    domain_systems_score = systems_calculation_service(domain_sorted_nodes)
    domain_sensitivity_factor = sensitivity_factor_calculation_service(domain_sorted_nodes)
    domain_impact_score = impact_calculation_service(domain_sorted_nodes)
    domain_compliance_factor = compilance_factor_calculation_service(domain_sorted_nodes)

    print(domain_complexity_score)
    print(domain_systems_score)
    print(domain_sensitivity_factor)
    print(domain_impact_score)
    print(domain_compliance_factor)
    print(project_legacy_value)


data = json.loads(sys.stdin.read())
files_list = [Path(f) for f in data["files"]]

main_entry(files_list)
