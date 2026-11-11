"""Модуль вычисления порядка загрузки и установки зависимостей (Этап 4)."""

from typing import Dict, List, Set


def compute_load_order(root: str, graph: Dict[str, List[str]]) -> List[str]:
    """Вычислить топологический порядок установки зависимостей (post-order DFS).

    Пакеты упорядочиваются от базовых к зависимым: пакет устанавливается
    только после того, как все его дочерние зависимости уже установлены.
    """
    order: List[str] = []
    visited: Set[str] = set()

    def dfs(node: str) -> None:
        if node in visited:
            return
        visited.add(node)
        for dep in graph.get(node, []):
            if dep in graph:
                dfs(dep)
        order.append(node)

    dfs(root)
    return order


# Псевдонимы на случай вызова под другими именами в модулях тестов
get_load_order = compute_load_order
topological_sort = compute_load_order