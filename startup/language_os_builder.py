from pathlib import Path

from tree_sitter import Language

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = PROJECT_ROOT / "build"
OUTPUT_PATH = BUILD_DIR / "languages.so"

BUILD_DIR.mkdir(parents=True, exist_ok=True)

Language.build_library(
    str(OUTPUT_PATH),
    [
        # Python
        str(PROJECT_ROOT / "tree_sitters/tree-sitter-python"),

        # JS / TS
        str(PROJECT_ROOT / "tree_sitters/tree-sitter-javascript"),
        str(PROJECT_ROOT / "tree_sitters/tree-sitter-typescript/typescript"),
        str(PROJECT_ROOT / "tree_sitters/tree-sitter-typescript/tsx"),

        # Backend languages
        str(PROJECT_ROOT / "tree_sitters/tree-sitter-php/php"),
        str(PROJECT_ROOT / "tree_sitters/tree-sitter-java"),
        str(PROJECT_ROOT / "tree_sitters/tree-sitter-go"),

        # Systems languages
        str(PROJECT_ROOT / "tree_sitters/tree-sitter-c"),
        str(PROJECT_ROOT / "tree_sitters/tree-sitter-cpp"),
        str(PROJECT_ROOT / "tree_sitters/tree-sitter-c-sharp"),

        # Mobile / modern
        str(PROJECT_ROOT / "tree_sitters/tree-sitter-kotlin"),
        str(PROJECT_ROOT / "tree_sitters/tree-sitter-swift"),
        str(PROJECT_ROOT / "tree_sitters/tree-sitter-dart"),

        # Scripting
        str(PROJECT_ROOT / "tree_sitters/tree-sitter-ruby"),
    ]
)