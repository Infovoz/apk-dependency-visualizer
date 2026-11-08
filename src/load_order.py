"""Модуль вычисления порядка загрузки и установки зависимостей."""

from typing import Dict, List, Set


def get_load_order(
    root: str,
    graph: Dict[str, List[str]],
) -> List[str]:
    """Вычислить порядок загрузки зависимостей для целевого пакета.

    Зависимости должны загружаться строго раньше зависящих от них пакетов.
    При наличии циклов цикл разрывается по уже посещенным узлам.

    Args:
        root: Имя целевого пакета.
        graph: Граф прямых зависимостей.

    Returns:
        Список пакетов в порядке их установки/загрузки.
    """
    order: List[str] = []
    visited: Set[str] = set()
    active_path: Set[str] = set()

    def dfs_post_order(node: str) -> None:
        """Вспомогательный обход для топологического упорядочивания.

        Args:
            node: Текущий обрабатываемый узел.
        """
        if node in visited or node in active_path:
            return

        active_path.add(node)
        for dep in graph.get(node, []):
            if dep not in visited:
                dfs_post_order(dep)

        active_path.remove(node)
        visited.add(node)
        order.append(node)

    dfs_post_order(root)
    return order