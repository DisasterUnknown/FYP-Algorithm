import re
from pathlib import Path
from src.lang_scanning.ts_loader import create_parser_with_language
from src.utils.import_graph_utils import append_graph_edge
from src.lang_scanning.tree_utils import first_header_line, name_from_field


class SwiftAnalyzer:
    def __init__(self, code_path: str):
        self.file_path = code_path
        self.source_code = self._load_source(code_path)

        self.parser, self.language = create_parser_with_language("swift")

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
            if node.kind() in ["import_declaration"]:
                text = self._text(node, self.source_code).strip()
                if text not in seen and text.startswith("import"):
                    seen.add(text)
                    imports.append(text)

        return imports

    def get_number_of_imports(self):
        return len(self.get_import_list())

    def _resolve_swift_import(self, line):
        match = re.search(r'import\s+"([^"]+)"', line)
        if not match:
            return None

        header = match.group(1)
        candidate = (Path(self.file_path).parent / header).resolve()
        if candidate.is_file():
            return candidate
        return None

    def get_graph_incoming_edges(self):
        edges = []
        seen = set()
        for line in self.get_import_list():
            append_graph_edge(
                edges,
                seen,
                self._resolve_swift_import(line),
                self.file_path,
            )
        return edges

    # ==================================================
    # classes
    def get_class_list(self):
        classes = []
        seen = set()
        for node in self._walk(self.tree.root_node()):
            if node.kind() in ("class_declaration", "struct_declaration", "protocol_declaration"):
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
            if node.kind() not in ("function_declaration", "initializer_declaration"):
                continue
            name = name_from_field(node, self.source_code)
            if name and name not in seen:
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
            "cryptokit",
            "commoncrypto",
            "crypto"
        ]
        crypto_calls = [
            "sha256",
            "sha1",
            "md5",
            "encrypt",
            "decrypt",
            "hmac",
            "aes"
        ]

        for node in self._walk(self.tree.root_node()):
            if node.kind() in ["import_declaration"]:
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
            if node.kind() in ("call_expression", "identifier"):
                for algo in crypto_algorithms:
                    if algo in text:
                        found.add(algo)

        return list(found)

    # ==================================================
    # database detection
    def get_contains_database_access(self):
        db_imports = [
            "coredata",
            "sqlite",
            "realm",
            "grdb"
        ]
        db_usage_patterns = [
            ".insert",
            ".fetch",
            ".delete",
            ".update",
            "select",
            "database"
        ]

        for node in self._walk(self.tree.root_node()):
            if node.kind() in ["import_declaration"]:
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
            if node.kind() in ("call_expression", "identifier"):
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
            "filemanager",
            "data(contentsOf:",
            "write(to:",
            "url(for:",
        ]
        for node in self._walk(self.tree.root_node()):
            text = self._text(node, self.source_code).lower()
            if any(p in text for p in file_patterns):
                return True

        return False


    # ==================================================
    # network access detection
    def get_contains_network_access(self):
        network_imports = [
            "urlsession",
            "alamofire"
        ]
        for node in self._walk(self.tree.root_node()):
            if node.kind() in ["import_declaration"]:
                text = self._text(node, self.source_code).lower()
                if any(n in text for n in network_imports):
                    return True

        network_calls = [
            "urlsession",
            ".dataTask",
            "alamofire",
            "websocket"
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
            "signin",
            "login",
            "authenticate",
            "token",
            "jwt"
        ]
        for node in self._walk(self.tree.root_node()):
            text = self._text(node, self.source_code).lower()
            if any(p in text for p in auth_patterns):
                return True

        return False

    # ==================================================
    # backuplogic detection
    def get_contains_backup_logic(self):
        backup_imports = [
            "cloudkit",
            "filemanager"
        ]
        for node in self._walk(self.tree.root_node()):
            if node.kind() in ["import_declaration"]:
                text = self._text(node, self.source_code).lower()
                if any(b in text for b in backup_imports):
                    return True

        backup_patterns = [
            "backup",
            "restore",
            "export",
            "sync"
        ]

        for node in self._walk(self.tree.root_node()):
            text = self._text(node, self.source_code).lower()
            if any(p in text for p in backup_patterns):
                return True

        return False








