"""Модуль генерации диаграмм PlantUML и вывода ASCII-дерева."""

from typing import Dict, List, Set


def generate_plantuml(
    root: str,
    graph: Dict[str, List[str]],
) -> str:
    """Сформировать текстовое описание графа на языке PlantUML.

    Args:
        root: Имя корневого пакета.
        graph: Словарь ребер графа зависимостей.

    Returns:
        Многострочная строка с кодом PlantUML.
    """
    lines: List[str] = [
        "@startuml",
        "skinparam monochrome true",
        "skinparam packageStyle rectangle",
        f'node "{root}" as root',
    ]

    has_edges = False
    for node, deps in graph.items():
        clean_node = node.replace('"', '\\"')
        for dep in deps:
            clean_dep = dep.replace('"', '\\"')
            lines.append(f'"{clean_node}" --> "{clean_dep}"')
            has_edges = True

    if not has_edges and root in graph:
        lines.append(f'note right of root : Нет зависимостей')

    lines.append("@enduml")
    return "\n".join(lines)


def render_ascii_tree(
    node: str,
    graph: Dict[str, List[str]],
    prefix: str = "",
    is_last: bool = True,
    visited_in_path: Set[str] = None,
) -> List[str]:
    """Сформировать представление дерева зависимостей в ASCII.

    Args:
        node: Текущий узел дерева.
        graph: Словарь зависимостей.
        prefix: Префикс текущей строки псевдографики.
        is_last: Флаг последнего потомка на текущем уровне.
        visited_in_path: Множество узлов текущей ветки для отлова циклов.

    Returns:
        Список строк ASCII-дерева.
    """
    if visited_in_path is None:
        visited_in_path = set()

    connector = "└── " if is_last else "├── "
    marker = " (цикл)" if node in visited_in_path else ""
    lines = [f"{prefix}{connector}{node}{marker}"]

    if node in visited_in_path:
        return lines

    new_visited = visited_in_path.copy()
    new_visited.add(node)

    deps = graph.get(node, [])
    new_prefix = prefix + ("    " if is_last else "│   ")

    for i, dep in enumerate(deps):
        child_is_last = i == (len(deps) - 1)
        child_lines = render_ascii_tree(
            dep,
            graph,
            new_prefix,
            child_is_last,
            new_visited,
        )
        lines.extend(child_lines)

    return lines