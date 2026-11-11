"""Главный модуль CLI-приложения для визуализации графа зависимостей."""

import argparse
import sys
from typing import Dict, List, Optional, Tuple

try:
    from src.apk_parser import fetch_and_parse_apkindex, parse_test_repo
    from src.graph_builder import build_dependency_graph
    from src.load_order import compute_load_order
    from src.visualizer import (
        encode_plantuml,
        generate_plantuml,
        render_ascii_tree,
    )
except ModuleNotFoundError:
    from apk_parser import fetch_and_parse_apkindex, parse_test_repo
    from graph_builder import build_dependency_graph
    from load_order import compute_load_order
    from visualizer import (
        encode_plantuml,
        generate_plantuml,
        render_ascii_tree,
    )


def parse_arguments() -> argparse.Namespace:
    """Создать парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Визуализатор графа зависимостей пакетов Alpine Linux."
    )
    parser.add_argument(
        "--package", required=True, type=str, help="Имя пакета."
    )
    parser.add_argument(
        "--repo", required=True, type=str, help="URL или путь к файлу."
    )
    parser.add_argument(
        "--test-mode", action="store_true", help="Режим тестового графа."
    )
    parser.add_argument(
        "--ascii-tree", action="store_true", help="Вывод в виде ASCII дерева."
    )
    parser.add_argument(
        "--max-depth", type=int, default=None, help="Лимит глубины обхода."
    )
    return parser.parse_args()


def validate_arguments(args: argparse.Namespace) -> None:
    """Проверить корректность аргументов командной строки."""
    if not args.package or not args.package.strip():
        raise ValueError("Имя пакета не может быть пустым.")
    if not args.repo or not args.repo.strip():
        raise ValueError("URL или путь к репозиторию не может быть пустым.")
    if args.max_depth is not None and args.max_depth <= 0:
        raise ValueError("Глубина должна быть положительным числом.")


def _print_stage1_info(args: argparse.Namespace) -> None:
    """Вывести параметры запуска этапа 1."""
    mode_text = (
        "Тестовый (файл)" if args.test_mode else "Основной (Alpine APK)"
    )
    depth_text = str(args.max_depth) if args.max_depth else "Без ограничений"
    print("\n" + "=" * 60)
    print(" [ЭТАП 1] ПАРСИНГ И ВАЛИДАЦИЯ АРГУМЕНТОВ CLI")
    print("=" * 60)
    print(f" -> Целевой пакет : {args.package}")
    print(f" -> Источник данных: {args.repo}")
    print(f" -> Режим работы   : {mode_text}")
    print(f" -> Лимит глубины  : {depth_text}")


def _load_stage2_data(
    repo: str, test_mode: bool, target: str
) -> Dict[str, List[str]]:
    """Загрузить и распарсить метаданные пакетов для этапа 2."""
    print("\n" + "=" * 60)
    print(" [ЭТАП 2] СБОР ДАННЫХ И ПАРСИНГ РЕПОЗИТОРИЯ")
    print("=" * 60)
    if test_mode:
        print("[*] Считывание тестового графа из файла...")
        repo_data = parse_test_repo(repo)
    else:
        print("[*] Загрузка и распаковка APKINDEX.tar.gz...")
        repo_data = fetch_and_parse_apkindex(repo)

    print(f"[OK] База загружена. Всего пакетов: {len(repo_data)}")
    direct_deps = repo_data.get(target, [])
    deps_str = ", ".join(direct_deps) if direct_deps else "(нет)"
    print(f"[*] Прямые зависимости '{target}': {deps_str}")
    return repo_data


def _build_stage3_graph(
    target: str, repo_data: Dict[str, List[str]], max_depth: Optional[int]
) -> Tuple[Dict[str, List[str]], List[Tuple[str, str]]]:
    """Построить граф зависимостей и вывести отчет этапа 3."""
    print("\n" + "=" * 60)
    print(" [ЭТАП 3] ПОСТРОЕНИЕ ГРАФА (РЕКУРСИВНЫЙ BFS)")
    print("=" * 60)
    print(f"[*] Запуск послойного обхода от корня '{target}'...")
    graph, cycles = build_dependency_graph(
        target, repo_data, max_depth=max_depth
    )
    print(f"[OK] Граф построен. Охвачено пакетов: {len(graph)}")
    for node, deps in graph.items():
        deps_repr = ", ".join(deps) if deps else "(нет)"
        print(f"    - {node} -> {deps_repr}")

    if cycles:
        print(f"\n[!] ВНИМАНИЕ: Найдено циклов: {len(cycles)}")
        for src, dst in cycles:
            print(f"    [ЦИКЛ] {src} -> {dst}")
    else:
        print("[OK] Циклических зависимостей не обнаружено.")
    return graph, cycles


def _print_stage4_order(target: str, graph: Dict[str, List[str]]) -> None:
    """Вычислить и отобразить топологический порядок для этапа 4."""
    print("\n" + "=" * 60)
    print(" [ЭТАП 4] ВЫЧИСЛЕНИЕ ПОРЯДКА УСТАНОВКИ (ТОПОЛОГИЧЕСКАЯ СОРТИРОВКА)")
    print("=" * 60)
    order = compute_load_order(target, graph)
    print("[*] Очередность установки пакетов (от базовых к зависимым):")
    for idx, pkg in enumerate(order, 1):
        flag = " (целевой)" if pkg == target else ""
        print(f"    {idx}. {pkg}{flag}")


def _render_stage5_views(
    target: str, graph: Dict[str, List[str]], ascii_tree: bool
) -> None:
    """Сгенерировать ASCII дерево и PlantUML URL для этапа 5."""
    print("\n" + "=" * 60)
    print(" [ЭТАП 5] ГЕНЕРАЦИЯ ВИЗУАЛИЗАЦИИ")
    print("=" * 60)
    if ascii_tree:
        print("[*] Дерево зависимостей (ASCII):")
        print("----------------------------------------")
        print("\n".join(render_ascii_tree(target, graph)))
        print("----------------------------------------\n")

    plantuml_code = generate_plantuml(target, graph)
    print("[*] Исходный код PlantUML:")
    print("----------------------------------------")
    print(plantuml_code)
    print("----------------------------------------")

    encoded = encode_plantuml(plantuml_code)
    url = f"https://www.plantuml.com/plantuml/svg/{encoded}"
    print(f"\n[*] Ссылка на готовую диаграмму (SVG):\n    {url}\n")
    print("[ЗАВЕРШЕНО] Анализ успешно выполнен.\n")


def run_pipeline(args: argparse.Namespace) -> None:
    """Выполнить все этапы конвейера анализа зависимостей."""
    validate_arguments(args)
    target = args.package.strip()
    _print_stage1_info(args)
    repo_data = _load_stage2_data(args.repo, args.test_mode, target)
    graph, _ = _build_stage3_graph(target, repo_data, args.max_depth)
    _print_stage4_order(target, graph)
    _render_stage5_views(target, graph, args.ascii_tree)


def main() -> None:
    """Главная точка входа в программу."""
    args = parse_arguments()
    try:
        run_pipeline(args)
    except ValueError as err:
        print(f"Ошибка конфигурации: {err}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as err:
        print(f"Ошибка файловой системы: {err}", file=sys.stderr)
        sys.exit(1)
    except Exception as err:
        print(f"Критическая ошибка выполнения: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()