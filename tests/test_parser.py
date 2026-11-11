"""Модульные тесты парсинга APKINDEX (Этап 2)."""

import unittest
from src.apk_parser import clean_dependency_name, parse_apkindex_content


class TestApkParser(unittest.TestCase):
    """Тестирование разбора пакетов и их зависимостей."""

    def test_clean_dependency_name(self) -> None:
        """Проверка очистки имен зависимостей от версий и префиксов."""
        self.assertEqual(clean_dependency_name("so:libc.musl.so"), "")
        self.assertEqual(clean_dependency_name("cmd:sh"), "")
        self.assertEqual(clean_dependency_name("pc:libssl"), "")
        self.assertEqual(
            clean_dependency_name("libssl3>=3.0.0"),
            "libssl3",
        )
        self.assertEqual(clean_dependency_name("zlib=1.2.11"), "zlib")
        self.assertEqual(clean_dependency_name("curl"), "curl")

    def test_parse_apkindex_content(self) -> None:
        """Проверка разбора структуры пакетов и их зависимостей."""
        raw_index = (
            "P:curl\n"
            "V:8.0.0\n"
            "D:libcurl so:libc.musl.so ca-certificates\n\n"
            "P:libcurl\n"
            "V:8.0.0\n"
            "D:libssl3>=3.0 zlib\n\n"
            "P:libssl3\n"
            "V:3.0.0\n"
            "D:\n"
        )
        repo = parse_apkindex_content(raw_index)
        self.assertIn("curl", repo)
        expected_curl = ["libcurl", "ca-certificates"]
        self.assertEqual(repo["curl"], expected_curl)
        self.assertEqual(repo["libcurl"], ["libssl3", "zlib"])
        self.assertEqual(repo["libssl3"], [])


if __name__ == "__main__":
    unittest.main()