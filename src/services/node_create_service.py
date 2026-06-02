from typing import List
from pathlib import Path
from src.model.file_node import FileNode
from src.lang_scanning.python_analyzer import PythonAnalyzer
from src.lang_scanning.javascript_analyzer import JavaScriptAnalyzer
from src.lang_scanning.typescript_analyzer import TypeScriptAnalyzer, TsxAnalyzer
from src.lang_scanning.php_analyzer import PhpAnalyzer
from src.lang_scanning.java_analyzer import JavaAnalyzer
from src.lang_scanning.go_analyzer import GoAnalyzer
from src.lang_scanning.c_analyzer import CAnalyzer
from src.lang_scanning.cpp_analyzer import CppAnalyzer
from src.lang_scanning.csharp_analyzer import CSharpAnalyzer
from src.lang_scanning.kotlin_analyzer import KotlinAnalyzer
from src.lang_scanning.swift_analyzer import SwiftAnalyzer
from src.lang_scanning.dart_analyzer import DartAnalyzer
from src.lang_scanning.ruby_analyzer import RubyAnalyzer

def language_support_checker_selector(file_extension: str, file_path: Path):
    file_extension = file_extension.lower()

    if file_extension == '.py':
        return PythonAnalyzer(code_path=str(file_path))
    elif file_extension in ['.js', '.jsx']:
        return JavaScriptAnalyzer(code_path=str(file_path))
    elif file_extension == '.ts':
        return TypeScriptAnalyzer(code_path=str(file_path))
    elif file_extension in ['.tsx']:
        return TsxAnalyzer(code_path=str(file_path))
    elif file_extension == '.php':
        return PhpAnalyzer(code_path=str(file_path))
    elif file_extension == '.java':
        return JavaAnalyzer(code_path=str(file_path))
    elif file_extension == '.go':
        return GoAnalyzer(code_path=str(file_path))
    elif file_extension in ['.c', '.h']:
        return CAnalyzer(code_path=str(file_path))
    elif file_extension in ['.cpp', '.cc', '.cxx', '.hpp', '.hh', '.hxx']:
        return CppAnalyzer(code_path=str(file_path))
    elif file_extension == '.cs':
        return CSharpAnalyzer(code_path=str(file_path))
    elif file_extension == '.kt':
        return KotlinAnalyzer(code_path=str(file_path))
    elif file_extension == '.swift':
        return SwiftAnalyzer(code_path=str(file_path))
    elif file_extension == '.dart':
        return DartAnalyzer(code_path=str(file_path))
    elif file_extension == '.rb':
        return RubyAnalyzer(code_path=str(file_path))
    else:
        return 'unsupported'

def file_analyzer(file_path: Path) -> FileNode:
    file_path_name = str(file_path).strip()
    file_name = Path(file_path).name
    file_extension = Path(file_path).suffix.lower()
    size_bytes = file_path.stat().st_size

    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
        lines = content.splitlines()
        lines_of_code = len(lines)
        blank_lines = sum(1 for line in lines if not line.strip())
    except Exception:
        lines_of_code = None
        blank_lines = None

    # langage specific data gathering
    language_class_node = language_support_checker_selector(file_extension, file_path)
    comment_lines = language_class_node.get_comment_lines()

    number_of_classes = language_class_node.get_number_of_classes()
    number_of_functions = language_class_node.get_number_of_functions()
    number_of_imports = language_class_node.get_number_of_imports()

    class_list = language_class_node.get_class_list()
    function_list = language_class_node.get_function_list()
    import_list = language_class_node.get_import_list()
    graph_incoming_edges = language_class_node.get_graph_incoming_edges()

    contains_crypto_usage = language_class_node.get_contains_crypto_usage()
    crypto_algorithm = language_class_node.get_crypto_algorithms()

    contains_database_access = language_class_node.get_contains_database_access()
    database_tables = language_class_node.get_database_tables()

    contains_file_access = language_class_node.get_contains_file_access()
    contains_network_access = language_class_node.get_contains_network_access()
    contains_auth_usage = language_class_node.get_contains_auth_usage()
    contains_backup_logic = language_class_node.get_contains_backup_logic()


    return FileNode(
        file_path=file_path_name,
        file_name=file_name,
        file_extension=file_extension,
        size_bytes=size_bytes,
        lines_of_code=lines_of_code,
        blank_lines=blank_lines,
        comment_lines=comment_lines,
        number_of_classes=number_of_classes,
        number_of_functions=number_of_functions,
        number_of_imports=number_of_imports,
        class_list=class_list,
        function_list=function_list,
        import_list=import_list,
        graph_incoming_edges=graph_incoming_edges,
        contains_crypto_usage=contains_crypto_usage,
        crypto_algorithm=crypto_algorithm,
        contains_database_access=contains_database_access,
        database_tables=database_tables,
        contains_file_access=contains_file_access,
        contains_network_access=contains_network_access,
        contains_auth_usage=contains_auth_usage,
        contains_backup_logic=contains_backup_logic
    )



def node_create_service(files_list: list[Path]):
    list_of_file_nodes: List[FileNode] = []

    for file_path in files_list:
        list_of_file_nodes.append(file_analyzer(file_path))

    return list_of_file_nodes
