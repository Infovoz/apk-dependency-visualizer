"""Модуль построения графа зависимостей с помощью рекурсивного BFS."""

from typing import Dict, List, Optional, Set, Tuple


def parse_test_repository(file_path: str) -> Dict[str, List[str]]:
    """Прочитать тестовое описание графа репозитория из файла.

    Формат строк: A: B C или A -> B, C

    Args:
        file_path: Путь к текстовому файлу.

    Returns:
        Словарь: имя пакета -> список зависимостей.
    """
    graph: Dict[str, List[str]] = {}
    with open(file_path, "r", encoding="utf-8") as file_handle:
        for raw_line in file_handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            separator = "->" if "->" in line else ":"
            if separator in line:
                src, dst = line.split(separator, 1)
                package = src.strip()
                tokens = (
                    dst.replace(",", " ")
                    .replace(";", " ")
                    .split()
                )
                graph[package] = [t.strip() for t in tokens if t.strip()]
            else:
                graph[line] = []
    return graph


def bfs_layer(
    current_layer: List[str],
    packages: Dict[str, List[str]],
    visited: Set[str],
    graph: Dict[str, List[str]],
    current_depth: int,
    max_depth: Optional[int],
    cycles: Set[Tuple[str, str]],
) -> None:
    """Рекурсивный шаг алгоритма BFS для обхода зависимостей по слоям.

    Args:
        current_layer: Узлы текущего уровня обхода.
        packages: Источник всех доступных пакетов и зависимостей.
        visited: Множество уже посещенных узлов.
        graph: Результирующий граф смежности.
        current_depth: Текущая глубина рекурсии.
        max_depth: Ограничение глубины.
        cycles: Множество обнаруженных циклических ребер.
    """
    if not current_layer:
        return
    if max_depth is not None and current_depth >= max_depth:
        return

    next_layer: List[str] = []

    for node in current_layer:
        deps = packages.get(node, [])
        if node not in graph:
            graph[node] = []

        for dep in deps:
            if dep not in graph[node]:
                graph[node].append(dep)

            if dep in visited:
                cycles.add((node, dep))
            else:
                visited.add(dep)
                next_layer.append(dep)

    bfs_layer(
        next_layer,
        packages,
        visited,
        graph,
        current_depth + 1,
        max_depth,
        cycles,
    )


def build_dependency_graph(
    root_package: str,
    packages: Dict[str, List[str]],
    max_depth: Optional[int] = None,
) -> Tuple[Dict[str, List[str]], Set[Tuple[str, str]]]:
    """Построить транзитивный граф зависимостей рекурсивным BFS.

    Args:
        root_package: Имя корневого пакета.
        packages: Словарь зависимостей репозитория.
        max_depth: Максимальная глубина обхода.

    Returns:
        Кортеж: (граф_смежности, множество_циклических_связей).
    """
    graph: Dict[str, List[str]] = {}
    visited: Set[str] = {root_package}
    cycles: Set[Tuple[str, str]] = set()

    bfs_layer(
        [root_package],
        packages,
        visited,
        graph,
        0,
        max_depth,
        cycles,
    )
    return graph, cycles