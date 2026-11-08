"""Модульные тесты для построения графа (Этап 3)."""

import unittest
from src.graph_builder import build_dependency_graph


class TestGraphBuilder(unittest.TestCase):
    """Тестирование рекурсивного BFS и обработки циклов."""

    def test_transitive_bfs(self) -> None:
        """Проверка транзитивного обхода в глубину по уровням."""
        packages = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": [],
            "D": [],
        }
        graph, cycles = build_dependency_graph("A", packages)
        self.assertEqual(len(cycles), 0)
        self.assertIn("A", graph)
        self.assertIn("B", graph)
        self.assertEqual(graph["A"], ["B", "C"])
        self.assertEqual(graph["B"], ["D"])

    def test_cycle_detection(self) -> None:
        """Проверка корректной фиксации циклической зависимости."""
        packages = {
            "A": ["B"],
            "B": ["C"],
            "C": ["A"],
        }
        graph, cycles = build_dependency_graph("A", packages)
        self.assertTrue(len(cycles) > 0)
        self.assertIn(("C", "A"), cycles)

    def test_max_depth_restriction(self) -> None:
        """Проверка ограничения глубины обхода."""
        packages = {
            "A": ["B"],
            "B": ["C"],
            "C": ["D"],
            "D": [],
        }
        graph, _ = build_dependency_graph("A", packages, max_depth=1)
        self.assertIn("A", graph)
        self.assertEqual(graph["A"], ["B"])
        self.assertNotIn("B", graph)


if __name__ == "__main__":
    unittest.main()