"""Модульные тесты для парсера APKINDEX (Этап 2)."""

import unittest
from src.apk_parser import clean_dependency_name, parse_apkindex_content


class TestApkParser(unittest.TestCase):
    """Тестирование разбора данных из APKINDEX."""

    def test_clean_dependency_name(self) -> None:
        """Проверка очистки имен зависимостей от версий и префиксов."""
        self.assertEqual(clean_dependency_name("ca-certificates"), "ca-certificates")
        self.assertEqual(clean_dependency_name("zlib>=1.2.11"), "zlib")
        self.assertEqual(clean_dependency_name("so:libc.musl-x86_64.so.1"), "")
        self.assertEqual(clean_dependency_name("cmd:sh"), "")

    def test_parse_apkindex_content(self) -> None:
        """Проверка разбора структуры пакетов и их зависимостей."""
        content = (
            "C:Q1\nP:curl\nV:8.0.1\nD:ca-certificates libcurl>=8.0.1 so:libc.so\n\n"
            "C:Q2\nP:libcurl\nV:8.0.1\nD:zlib openssl\n"
        )
        result = parse_apkindex_content(content)
        self.assertIn("curl", result)
        self.assertEqual(result["curl"], ["ca-certificates", "libcurl"])
        self.assertEqual(result["libcurl"], ["zlib", "openssl"])


if __name__ == "__main__":
    unittest.main()