from src.lang_scanning.ts_loader import create_parser_with_language
from src.lang_scanning.javascript_analyzer import JavaScriptAnalyzer


class TypeScriptAnalyzer(JavaScriptAnalyzer):
    """TypeScript shares the JavaScript tree-sitter grammar (with types)."""

    def __init__(self, code_path: str):
        self.file_path = code_path
        self.source_code = self._load_source(code_path)

        self.parser, self.language = create_parser_with_language("typescript")

        self.tree = self._parse(self.source_code)


class TsxAnalyzer(TypeScriptAnalyzer):
    def __init__(self, code_path: str):
        self.file_path = code_path
        self.source_code = self._load_source(code_path)

        self.parser, self.language = create_parser_with_language("tsx")

        self.tree = self._parse(self.source_code)







