import re
from pathlib import Path
from tree_sitter import Language, Parser
from src.utils.import_graph_utils import append_graph_edge, first_existing
from src.lang_scanning.tree_utils import first_header_line, name_from_definition


class PythonAnalyzer:
    def __init__(self, code_path: str):
        self.file_path = code_path
        self.source_code = self._load_source(code_path)

        self.language = Language('build/languages.so', "python")
        self.parser = Parser()
        self.parser.set_language(self.language)

        self.tree = self._parse(self.source_code)

    # ==================================================
    # core helpers
    def _parse(self, source_code: str):
        return self.parser.parse(bytes(source_code, "utf8"))

    def _walk(self, node):
        yield node
        for child in node.children:
            yield from self._walk(child)

    def _text(self, node, source_code: str) -> str:
        return source_code[node.start_byte:node.end_byte]

    def _load_source(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    # ==================================================
    # imports
    def get_import_list(self):
        imports = []
        seen = set()
        for node in self._walk(self.tree.root_node):
            if node.type in ["import_statement", "import_from_statement"]:
                text = self._text(node, self.source_code).strip()
                if text not in seen and text.startswith(('import ', 'from ')):
                    seen.add(text)
                    imports.append(text)

        return imports

    def get_number_of_imports(self):
        return len(self.get_import_list())

    def _resolve_python_import(self, stmt):
        current_file = Path(self.file_path)
        current_dir = current_file.parent

        if stmt.startswith("from "):
            match = re.match(r"from\s+(\S+)\s+import", stmt)
            if not match:
                return None
            module = match.group(1)
        elif stmt.startswith("import "):
            module = stmt.split()[1].split(",")[0].strip()
        else:
            return None

        if module.startswith("."):
            level = len(module) - len(module.lstrip("."))
            module_rest = module[level:].replace(".", "/")
            base = current_dir
            for _ in range(level - 1):
                base = base.parent
            target = base / module_rest if module_rest else base
        else:
            parts = module.replace(".", "/")
            for root in [current_dir, *current_file.parents]:
                target = root / parts
                found = first_existing([
                    target.with_suffix(".py"),
                    target / "__init__.py",
                ])
                if found:
                    return found
            return None

        return first_existing([
            target.with_suffix(".py"),
            target / "__init__.py",
        ])

    def get_graph_incoming_edges(self):
        edges = []
        seen = set()
        for stmt in self.get_import_list():
            append_graph_edge(
                edges,
                seen,
                self._resolve_python_import(stmt),
                self.file_path,
            )
        return edges

    # ==================================================
    # classes
    def get_class_list(self):
        classes = []
        seen = set()
        for node in self._walk(self.tree.root_node):
            if node.type == "class_definition":
                text = self._text(node, self.source_code).strip()
                first_line = first_header_line(text, (":", "{"))
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
        for node in self._walk(self.tree.root_node):
            target = None
            if node.type == "function_definition":
                target = node
            elif node.type == "decorated_definition":
                for child in node.children:
                    if child.type == "function_definition":
                        target = child
                        break
            if target is None:
                continue
            name = name_from_definition(target, self.source_code)
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
        for node in self._walk(self.tree.root_node):
            if "comment" in node.type:
                start_line = node.start_point[0]
                end_line = node.end_point[0]
                for i in range(start_line, end_line + 1):
                    lines.add(i)

        return len(lines)

    # ==================================================
    # crypto detection
    def get_contains_crypto_usage(self):
        crypto_imports = [
            "hashlib",
            "cryptography",
            "pycryptodome",
            "Crypto"
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

        for node in self._walk(self.tree.root_node):
            if node.type in ["import_statement", "import_from_statement"]:
                text = self._text(node, self.source_code).lower()
                if any(i in text for i in crypto_imports):
                    return True
        for node in self._walk(self.tree.root_node):
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
        for node in self._walk(self.tree.root_node):
            text = self._text(node, self.source_code).lower()
            if node.type in ["call", "identifier"]:
                for algo in crypto_algorithms:
                    if algo in text:
                        found.add(algo)

        return list(found)

    # ==================================================
    # database detection
    def get_contains_database_access(self):
        db_imports = [
            "sqlite3",
            "sqlalchemy",
            "pymongo",
            "psycopg2"
        ]
        db_usage_patterns = [
            ".execute",
            ".cursor",
            ".commit",
            "select",
            "insert",
            "database"
        ]

        for node in self._walk(self.tree.root_node):
            if node.type in ["import_statement", "import_from_statement"]:
                text = self._text(node, self.source_code).lower()
                if any(d in text for d in db_imports):
                    return True
        for node in self._walk(self.tree.root_node):
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
        for node in self._walk(self.tree.root_node):
            if node.type in ["call", "identifier"]:
                text = self._text(node, self.source_code).lower()

                if any(op in text for op in db_operations):
                    for table in known_tables:
                        if table in text:
                            found.add(table)

        return list(found)

    # ==================================================
    # file access detection
    def get_contains_file_access(self):
        for node in self._walk(self.tree.root_node):
            if node.type in ["import_statement", "import_from_statement"]:
                text = self._text(node, self.source_code).lower()
                if any(m in text for m in ["os", "pathlib", "shutil", "io"]):
                    return True

        file_patterns = [
            "open(",
            "pathlib",
            "os.path",
            "read_bytes",
            "write_bytes",
            "shutil.",
        ]
        for node in self._walk(self.tree.root_node):
            text = self._text(node, self.source_code).lower()
            if any(p in text for p in file_patterns):
                return True

        return False


    # ==================================================
    # network access detection
    def get_contains_network_access(self):
        network_imports = [
            "requests",
            "httpx",
            "urllib",
            "aiohttp",
            "socket"
        ]
        for node in self._walk(self.tree.root_node):
            if node.type in ["import_statement", "import_from_statement"]:
                text = self._text(node, self.source_code).lower()
                if any(n in text for n in network_imports):
                    return True

        network_calls = [
            "requests.get",
            "requests.post",
            "httpx.",
            "urllib.request",
            "socket."
        ]
        for node in self._walk(self.tree.root_node):
            text = self._text(node, self.source_code).lower()
            if any(c in text for c in network_calls):
                return True

        return False

    # ==================================================
    # auth usage detection
    def get_contains_auth_usage(self):
        for node in self._walk(self.tree.root_node):
            if node.type in ["import_statement", "import_from_statement"]:
                text = self._text(node, self.source_code).lower()
                if any(m in text for m in ["jwt", "passlib", "authlib", "firebase_admin"]):
                    return True

        auth_patterns = [
            "login",
            "authenticate",
            "auth.",
            "token",
            "jwt",
            "password",
        ]
        for node in self._walk(self.tree.root_node):
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
            "export_data",
            "import_data",
        ]

        for node in self._walk(self.tree.root_node):
            text = self._text(node, self.source_code).lower()
            if any(p in text for p in backup_patterns):
                return True

        return False

