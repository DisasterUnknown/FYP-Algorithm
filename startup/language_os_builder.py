from tree_sitter_language_pack import get_parser


SUPPORTED_LANGUAGES = [
    "python",
    "javascript",
    "typescript",
    "tsx",
    "php",
    "java",
    "go",
    "c",
    "cpp",
    "csharp",
    "kotlin",
    "swift",
    "dart",
    "ruby",
]


def main():
    missing = []
    for language in SUPPORTED_LANGUAGES:
        try:
            get_parser(language)
        except Exception:
            missing.append(language)

    if missing:
        raise RuntimeError(f"Missing tree-sitter grammars: {', '.join(missing)}")

    print("Tree-sitter language pack ready for all configured languages.")


if __name__ == "__main__":
    main()