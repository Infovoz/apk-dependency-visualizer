"""Модуль загрузки и парсинга репозиториев (Этап 2)."""

import io
import re
import tarfile
import urllib.request
from typing import Dict, List


def clean_dependency_name(raw_dep: str) -> str:
    """Очистить имя зависимости от версий и префиксов (so:, cmd:, pc:)."""
    clean = raw_dep.strip()
    if clean.startswith(("so:", "cmd:", "pc:")):
        return ""
    clean = re.split(r"[><=~]", clean)[0].strip()
    return clean


def parse_apkindex_content(content: str) -> Dict[str, List[str]]:
    """Распарсить текстовое содержимое APKINDEX."""
    repo: Dict[str, List[str]] = {}
    current_pkg = None
    current_deps: List[str] = []

    for line in content.splitlines():
        line = line.strip()
        if not line:
            if current_pkg:
                repo[current_pkg] = current_deps
                current_pkg = None
                current_deps = []
            continue

        if line.startswith("P:"):
            current_pkg = line[2:].strip()
        elif line.startswith("D:"):
            raw_deps = line[2:].strip().split()
            current_deps = [
                dep for d in raw_deps if (dep := clean_dependency_name(d))
            ]

    if current_pkg:
        repo[current_pkg] = current_deps

    return repo


def fetch_and_parse_apkindex(url: str) -> Dict[str, List[str]]:
    """Скачать APKINDEX.tar.gz по сети и извлечь зависимости."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        tar_bytes = io.BytesIO(resp.read())

    with tarfile.open(fileobj=tar_bytes, mode="r:gz") as tar:
        member = tar.extractfile("APKINDEX")
        if not member:
            raise ValueError("Файл APKINDEX не найден внутри архива.")
        content = member.read().decode("utf-8", errors="ignore")

    return parse_apkindex_content(content)


def parse_test_repo(filepath: str) -> Dict[str, List[str]]:
    """Считать тестовый репозиторий из локального текстового файла."""
    repo: Dict[str, List[str]] = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            sep = ":" if ":" in line else "->"
            if sep in line:
                pkg, deps_part = line.split(sep, 1)
                pkg = pkg.strip()
                deps = [d.strip() for d in deps_part.split() if d.strip()]
                repo[pkg] = deps
            else:
                repo[line] = []
    return repo