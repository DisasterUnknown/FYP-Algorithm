from tree_sitter import Language, Parser
from src.lang_scanning.javascript_analyzer import JavaScriptAnalyzer


class TypeScriptAnalyzer(JavaScriptAnalyzer):
    """TypeScript shares the JavaScript tree-sitter grammar (with types)."""

    def __init__(self, code_path: str):
        self.file_path = code_path
        self.source_code = self._load_source(code_path)

        self.language = Language('build/languages.so', "typescript")
        self.parser = Parser()
        self.parser.set_language(self.language)

        self.tree = self._parse(self.source_code)


class TsxAnalyzer(TypeScriptAnalyzer):
    def __init__(self, code_path: str):
        self.file_path = code_path
        self.source_code = self._load_source(code_path)

        self.language = Language('build/languages.so', "tsx")
        self.parser = Parser()
        self.parser.set_language(self.language)

        self.tree = self._parse(self.source_code)
