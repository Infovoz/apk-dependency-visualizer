"""Модульные тесты порядка загрузки зависимостей (Этап 4)."""

import unittest
from src.load_order import get_load_order


class TestLoadOrder(unittest.TestCase):
    """Тестирование корректности порядка установки пакетов."""

    def test_linear_order(self) -> None:
        """Проверка порядка для линейного графа A -> B -> C."""
        graph = {
            "A": ["B"],
            "B": ["C"],
            "C": [],
        }
        order = get_load_order("A", graph)
        self.assertEqual(order, ["C", "B", "A"])

    def test_branching_order(self) -> None:
        """Проверка порядка для разветвленного графа."""
        graph = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": [],
        }
        order = get_load_order("A", graph)
        self.assertTrue(order.index("D") < order.index("B"))
        self.assertTrue(order.index("D") < order.index("C"))
        self.assertEqual(order[-1], "A")

    def test_cycle_order_safety(self) -> None:
        """Проверка отсутствия зацикливания при наличии цикла."""
        graph = {
            "A": ["B"],
            "B": ["A"],
        }
        order = get_load_order("A", graph)
        self.assertEqual(set(order), {"A", "B"})


if __name__ == "__main__":
    unittest.main()