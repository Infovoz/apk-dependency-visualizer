"""Модуль генерации диаграмм PlantUML и вывода ASCII-дерева."""

import string
import zlib
from typing import Dict, List, Set

PLANTUML_ALPHABET = (
    string.digits + string.ascii_uppercase + string.ascii_lowercase + "-_"
)


def _encode_6bit(byte_val: int) -> str:
    return PLANTUML_ALPHABET[byte_val & 0x3F]


def encode_plantuml(plantuml_text: str) -> str:
    """Закодировать текст PlantUML в URL-хэш."""
    utf8_bytes = plantuml_text.encode("utf-8")
    compressor = zlib.compressobj(
        level=9,
        method=zlib.DEFLATED,
        wbits=-15,
        memLevel=8,
        strategy=zlib.Z_DEFAULT_STRATEGY,
    )
    compressed = compressor.compress(utf8_bytes) + compressor.flush()

    res = []
    i = 0
    while i < len(compressed):
        b1 = compressed[i]
        b2 = compressed[i + 1] if i + 1 < len(compressed) else 0
        b3 = compressed[i + 2] if i + 2 < len(compressed) else 0

        res.append(_encode_6bit(b1 >> 2))
        res.append(_encode_6bit(((b1 & 0x3) << 4) | (b2 >> 4)))
        res.append(_encode_6bit(((b2 & 0xF) << 2) | (b3 >> 6)))
        res.append(_encode_6bit(b3 & 0x3F))
        i += 3
    return "".join(res)


def generate_plantuml(
    root: str,
    graph: Dict[str, List[str]],
) -> str:
    """Сформировать текстовое описание графа на языке PlantUML."""
    lines: List[str] = [
        "@startuml",
        "!theme plain",
        "skinparam dpi 150",
        "skinparam defaultFontName sans-serif",
        "skinparam packageStyle rectangle",
        "skinparam roundCorner 8",
        f'node "{root}" as root #LightSkyBlue',
    ]

    has_edges = False
    for node, deps in graph.items():
        clean_node = node.replace('"', '\\"')
        for dep in deps:
            clean_dep = dep.replace('"', '\\"')
            lines.append(f'"{clean_node}" --> "{clean_dep}"')
            has_edges = True

    if not has_edges and root in graph:
        lines.append("note right of root : Пакет не имеет зависимостей")

    lines.append("@enduml")
    return "\n".join(lines)


def _get_node_tag(
    node: str,
    graph: Dict[str, List[str]],
    visited: Set[str],
    depth: int,
) -> str:
    """Определить служебную метку для узла ASCII дерева."""
    if depth == 0:
        return " [ROOT]"
    if node in visited:
        return " [ЦИКЛ!]"
    if not graph.get(node):
        return " [LEAF]"
    return ""


def render_ascii_tree(
    node: str,
    graph: Dict[str, List[str]],
    prefix: str = "",
    is_last: bool = True,
    visited_in_path: Set[str] = None,
    depth: int = 0,
) -> List[str]:
    """Сформировать представление дерева зависимостей в ASCII."""
    if visited_in_path is None:
        visited_in_path = set()

    connector = "└── " if is_last else "├── "
    tag = _get_node_tag(node, graph, visited_in_path, depth)
    lines = [f"{prefix}{connector}{node}{tag}"]

    if node in visited_in_path:
        return lines

    new_visited = visited_in_path.copy()
    new_visited.add(node)
    deps = graph.get(node, [])
    new_prefix = prefix + ("    " if is_last else "│   ")

    for i, dep in enumerate(deps):
        child_is_last = i == (len(deps) - 1)
        lines.extend(
            render_ascii_tree(
                dep,
                graph,
                new_prefix,
                child_is_last,
                new_visited,
                depth + 1,
            )
        )
    return lines