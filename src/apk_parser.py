"""Модуль загрузки и разбора зависимостей пакетов Alpine Linux apk."""

import io
import tarfile
import urllib.request
from typing import Dict, List


def clean_dependency_name(dep: str) -> str:
    """Очистить имя зависимости от версий и служебных префиксов.

    Args:
        dep: Исходная строка зависимости из APKINDEX.

    Returns:
        Имя пакета или пустая строка, если это виртуальный символ.
    """
    token = dep.strip()
    if not token or token.startswith("so:") or token.startswith("cmd:"):
        return ""
    for op in ("<=", ">=", "=", "<", ">", "~"):
        if op in token:
            token = token.split(op)[0].strip()
            break
    return token


def parse_apkindex_content(content: str) -> Dict[str, List[str]]:
    """Разобрать текстовое содержимое файла APKINDEX.

    Args:
        content: Распакованный текст файла APKINDEX.

    Returns:
        Словарь: имя пакета -> список прямых зависимостей.
    """
    packages: Dict[str, List[str]] = {}
    blocks = content.strip().split("\n\n")

    for block in blocks:
        lines = block.splitlines()
        pkg_name = ""
        deps: List[str] = []
        for line in lines:
            if line.startswith("P:"):
                pkg_name = line[2:].strip()
            elif line.startswith("D:"):
                raw_deps = line[2:].strip().split()
                for dep in raw_deps:
                    cleaned = clean_dependency_name(dep)
                    if cleaned and cleaned not in deps:
                        deps.append(cleaned)
        if pkg_name:
            packages[pkg_name] = deps

    return packages


def fetch_apkindex(repo_url_or_path: str) -> Dict[str, List[str]]:
    """Загрузить и распаковать APKINDEX по URL или из локального файла.

    Args:
        repo_url_or_path: URL или путь к архиву APKINDEX.tar.gz.

    Returns:
        Словарь зависимостей всех пакетов репозитория.
    """
    if repo_url_or_path.startswith("http://") or repo_url_or_path.startswith(
        "https://"
    ):
        request = urllib.request.Request(
            repo_url_or_path,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urllib.request.urlopen(request) as response:
            archive_bytes = response.read()
    else:
        with open(repo_url_or_path, "rb") as file_handle:
            archive_bytes = file_handle.read()

    with tarfile.open(fileobj=io.BytesIO(archive_bytes), mode="r:gz") as tar:
        index_member = tar.extractfile("APKINDEX")
        if index_member is None:
            raise ValueError("Файл APKINDEX не найден внутри архива.")
        text_content = index_member.read().decode("utf-8", errors="replace")

    return parse_apkindex_content(text_content)