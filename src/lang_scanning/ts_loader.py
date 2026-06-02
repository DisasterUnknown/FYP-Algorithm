from tree_sitter_language_pack import get_language, get_parser


def create_parser_with_language(language_name: str):
    """
    Return a parser/language pair backed by the language-pack grammars.
    Keeps all analyzers on a single, up-to-date grammar source.
    """
    parser = get_parser(language_name)
    language = get_language(language_name)
    return parser, language

