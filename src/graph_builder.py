"""Модуль построения графа зависимостей с помощью BFS (Этап 3)."""

from collections import deque
from typing import Dict, List, Optional, Set, Tuple


def _process_queue_level(
    queue: deque,
    repo_data: Dict[str, List[str]],
    graph: Dict[str, List[str]],
    visited: Set[str],
    cycles: List[Tuple[str, str]],
) -> None:
    """Обработать один уровень очереди BFS."""
    current_pkg, current_depth = queue.popleft()
    if current_pkg not in graph:
        graph[current_pkg] = []

    deps = repo_data.get(current_pkg, [])
    for dep in deps:
        if dep in visited:
            cycles.append((current_pkg, dep))
        else:
            visited.add(dep)
            queue.append((dep, current_depth + 1))
        graph[current_pkg].append(dep)


def build_dependency_graph(
    target: str,
    repo_data: Dict[str, List[str]],
    max_depth: Optional[int] = None,
) -> Tuple[Dict[str, List[str]], List[Tuple[str, str]]]:
    """Построить граф зависимостей рекурсивным послойным BFS."""
    graph: Dict[str, List[str]] = {}
    cycles: List[Tuple[str, str]] = []
    visited: Set[str] = {target}
    queue: deque = deque([(target, 0)])

    while queue:
        current_pkg, current_depth = queue[0]
        if max_depth is not None and current_depth >= max_depth:
            queue.popleft()
            continue

        _process_queue_level(queue, repo_data, graph, visited, cycles)

    return graph, cycles