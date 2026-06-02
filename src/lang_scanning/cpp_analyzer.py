import re
from pathlib import Path
from src.lang_scanning.ts_loader import create_parser_with_language
from src.utils.import_graph_utils import append_graph_edge
from src.lang_scanning.tree_utils import first_header_line


class CppAnalyzer:
    def __init__(self, code_path: str):
        self.file_path = code_path
        self.source_code = self._load_source(code_path)

        self.parser, self.language = create_parser_with_language("cpp")

        self.tree = self._parse(self.source_code)

    # ==================================================
    # core helpers
    def _parse(self, source_code: str):
        return self.parser.parse(source_code)

    def _walk(self, node):
        yield node
        for i in range(node.child_count()):
            child = node.child(i)
            yield from self._walk(child)

    def _text(self, node, source_code: str) -> str:
        return source_code[node.start_byte():node.end_byte()]

    def _load_source(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    # ==================================================
    # imports
    def get_import_list(self):
        imports = []
        seen = set()
        for node in self._walk(self.tree.root_node()):
            if node.kind() in ["preproc_include", "import_declaration"]:
                text = self._text(node, self.source_code).strip()
                if text not in seen:
                    seen.add(text)
                    imports.append(text)

        return imports

    def get_number_of_imports(self):
        return len(self.get_import_list())

    def _resolve_cpp_include(self, line):
        match = re.search(r'#include\s+"([^"]+)"', line)
        if not match:
            return None

        header = match.group(1)
        current_dir = Path(self.file_path).parent
        candidate = (current_dir / header).resolve()
        if candidate.is_file():
            return candidate

        for parent in Path(self.file_path).parents:
            include_path = parent / "include" / header
            if include_path.is_file():
                return include_path
        return None

    def get_graph_incoming_edges(self):
        edges = []
        seen = set()
        for line in self.get_import_list():
            append_graph_edge(
                edges,
                seen,
                self._resolve_cpp_include(line),
                self.file_path,
            )
        return edges

    # ==================================================
    # classes
    def get_class_list(self):
        classes = []
        seen = set()
        for node in self._walk(self.tree.root_node()):
            if node.kind() in ["class_specifier", "struct_specifier"]:
                text = self._text(node, self.source_code).strip()
                first_line = first_header_line(text)
                if first_line not in seen:
                    seen.add(first_line)
                    classes.append(first_line)

        return classes

    def get_number_of_classes(self):
        return len(self.get_class_list())

    # ==================================================
    # functions / methods
    def get_function_list(self):
        functions = []
        seen = set()
        for node in self._walk(self.tree.root_node()):
            if node.kind() in ["function_definition"]:
                text = self._text(node, self.source_code).strip()
                if "(" in text:
                    name = text.split('(')[0].split()[-1].strip()
                    if name not in seen:
                        seen.add(name)
                        functions.append(name)

        return functions

    def get_number_of_functions(self):
        return len(self.get_function_list())

    # ==================================================
    # comments
    def get_comment_lines(self):
        lines = set()
        for node in self._walk(self.tree.root_node()):
            if "comment" in node.kind():
                start_line = node.start_position().row
                end_line = node.end_position().row
                for i in range(start_line, end_line + 1):
                    lines.add(i)

        return len(lines)

    # ==================================================
    # crypto detection
    def get_contains_crypto_usage(self):
        crypto_imports = [
            "#include <openssl",
            "crypto",
            "openssl"
        ]
        crypto_calls = [
            "sha256",
            "sha1",
            "md5",
            "aes",
            "rsa",
            "hmac",
            "encrypt",
            "decrypt"
        ]

        for node in self._walk(self.tree.root_node()):
            if node.kind() in ["preproc_include", "import_declaration"]:
                text = self._text(node, self.source_code).lower()
                if any(i in text for i in crypto_imports):
                    return True
        for node in self._walk(self.tree.root_node()):
            text = self._text(node, self.source_code).lower()
            if any(c in text for c in crypto_calls):
                return True

        return False

    def get_crypto_algorithms(self):
        crypto_algorithms = {
            "sha1", "sha256", "sha512", "md5",
            "aes", "rsa", "ecdsa", "hmac"
        }

        found = set()
        for node in self._walk(self.tree.root_node()):
            text = self._text(node, self.source_code).lower()
            if node.kind() in ["call_expression", "identifier"]:
                for algo in crypto_algorithms:
                    if algo in text:
                        found.add(algo)

        return list(found)

    # ==================================================
    # database detection
    def get_contains_database_access(self):
        db_imports = [
            "sqlite",
            "mysql",
            "postgres",
            "mongodb"
        ]
        db_usage_patterns = [
            "select",
            "insert",
            "update",
            "delete",
            "query"
        ]

        for node in self._walk(self.tree.root_node()):
            if node.kind() in ["preproc_include", "import_declaration"]:
                text = self._text(node, self.source_code).lower()
                if any(d in text for d in db_imports):
                    return True
        for node in self._walk(self.tree.root_node()):
            text = self._text(node, self.source_code).lower()
            if any(p in text for p in db_usage_patterns):
                return True

        return False

    def get_database_tables(self):
        known_tables = [
            "users",
            "transactions",
            "budget",
            "categories",
            "settings"
        ]
        db_operations = [
            "insert",
            "query",
            "update",
            "delete",
            "select",
            "where",
            "from"
        ]

        found = set()
        for node in self._walk(self.tree.root_node()):
            if node.kind() in ["call_expression", "identifier"]:
                text = self._text(node, self.source_code).lower()

                if any(op in text for op in db_operations):
                    for table in known_tables:
                        if table in text:
                            found.add(table)

        return list(found)

    # ==================================================
    # file access detection
    def get_contains_file_access(self):
        file_patterns = [
            "fopen",
            "fread",
            "fwrite",
            "ifstream",
            "ofstream",
        ]
        for node in self._walk(self.tree.root_node()):
            text = self._text(node, self.source_code).lower()
            if any(p in text for p in file_patterns):
                return True

        return False


    # ==================================================
    # network access detection
    def get_contains_network_access(self):
        network_calls = [
            "socket",
            "connect",
            "send",
            "recv",
            "http",
            "curl"
        ]
        for node in self._walk(self.tree.root_node()):
            text = self._text(node, self.source_code).lower()
            if any(c in text for c in network_calls):
                return True

        return False

    # ==================================================
    # auth usage detection
    def get_contains_auth_usage(self):
        auth_patterns = [
            "login",
            "auth",
            "token",
            "jwt",
            "password"
        ]
        for node in self._walk(self.tree.root_node()):
            text = self._text(node, self.source_code).lower()
            if any(p in text for p in auth_patterns):
                return True

        return False

    # ==================================================
    # backuplogic detection
    def get_contains_backup_logic(self):
        backup_patterns = [
            "backup",
            "restore",
            "sync",
        ]

        for node in self._walk(self.tree.root_node()):
            text = self._text(node, self.source_code).lower()
            if any(p in text for p in backup_patterns):
                return True

        return False








