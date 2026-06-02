"""Helpers for resolving local imports to graph_incoming_edges file paths."""
import re
from pathlib import Path
from typing import Iterable, List, Optional


def format_graph_path(path: Path, reference_file_path: str) -> str:
    resolved = path.resolve()
    text = str(resolved)
    if "/" in reference_file_path and "\\" in text:
        text = resolved.as_posix()
    return text


def first_existing(candidates: Iterable[Path]) -> Optional[Path]:
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def walk_up_for_marker(start: Path, marker: str) -> Optional[Path]:
    current = start.resolve().parent
    for _ in range(50):
        if (current / marker).is_file():
            return current
        if current.parent == current:
            break
        current = current.parent
    return None


def quoted_paths_from_import_line(line: str) -> List[str]:
    return re.findall(r"""['"]([^'"]+)['"]""", line)


def append_graph_edge(
    edges: List[str],
    seen: set,
    path: Optional[Path],
    reference_file_path: str,
) -> None:
    if path is None or not path.is_file():
        return
    key = format_graph_path(path, reference_file_path)
    if key not in seen:
        seen.add(key)
        edges.append(key)
