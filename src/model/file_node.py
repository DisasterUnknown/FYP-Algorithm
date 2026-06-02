from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FileNode:
    # required
    file_path: str
    file_name: str

    # basic metadata
    file_extension: Optional[str] = None
    size_bytes: Optional[int] = None
    lines_of_code: Optional[int] = None
    comment_lines: Optional[int] = None
    blank_lines: Optional[int] = None

    # structure and content
    number_of_classes: Optional[int] = None
    number_of_functions: Optional[int] = None  
    number_of_imports: Optional[int] = None

    class_list: Optional[List[str]] = field(default_factory=list)
    function_list: Optional[List[str]] = field(default_factory=list)
    import_list: Optional[List[str]] = field(default_factory=list)

    # security flags (bool default = 0 / False)
    contains_crypto_usage: bool = False
    crypto_algorithm: Optional[List[str]] = field(default_factory=list)

    contains_database_access: bool = False
    database_tables: Optional[List[str]] = field(default_factory=list)

    contains_file_access: bool = False
    contains_network_access: bool = False
    contains_auth_usage: bool = False
    contains_backup_logic: bool = False

    graph_incoming_edges: Optional[List[str]] = field(default_factory=list)
    graph_outgoing_edges: Optional[List[str]] = field(default_factory=list)