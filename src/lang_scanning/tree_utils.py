"""Tree-sitter helpers shared by language analyzers."""


def first_header_line(text: str, delimiters=("{", ":")) -> str:
    line = text.splitlines()[0] if text else text
    for delimiter in delimiters:
        if delimiter in line:
            line = line.split(delimiter)[0]
    return line.strip()


def name_from_field(node, source_code: str, field: str = "name"):
    child = node.child_by_field_name(field)
    if child is None:
        return None
    return source_code[child.start_byte():child.end_byte()].strip()


def name_from_definition(node, source_code: str, identifier_types=("identifier",)):
    name = name_from_field(node, source_code, "name")
    if name:
        return name
    for i in range(node.child_count()):
        child = node.child(i)
        if child.kind() in identifier_types:
            return source_code[child.start_byte():child.end_byte()].strip()
    return None



