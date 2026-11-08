"""Модульные тесты генерации визуализации (Этап 5)."""

import unittest
from src.visualizer import generate_plantuml, render_ascii_tree


class TestVisualizer(unittest.TestCase):
    """Тестирование генерации диаграмм PlantUML и ASCII дерева."""

    def test_plantuml_structure(self) -> None:
        """Проверка наличия служебных тегов PlantUML."""
        graph = {"A": ["B"], "B": []}
        uml = generate_plantuml("A", graph)
        self.assertTrue(uml.startswith("@startuml"))
        self.assertTrue(uml.endswith("@enduml"))
        self.assertIn('"A" --> "B"', uml)

    def test_ascii_tree_rendering(self) -> None:
        """Проверка генерации псевдографики."""
        graph = {"A": ["B"], "B": []}
        lines = render_ascii_tree("A", graph)
        self.assertTrue(any("A" in line for line in lines))
        self.assertTrue(any("└── B" in line for line in lines))


if __name__ == "__main__":
    unittest.main()