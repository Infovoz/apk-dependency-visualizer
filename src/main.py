"""Точка входа CLI для визуализатора зависимостей."""

import argparse
import sys
from src.visualizer import generate_plantuml, render_ascii_tree
try:
    from src.apk_parser import fetch_apkindex
    from src.graph_builder import (
        build_dependency_graph,
        parse_test_repository,
    )
    from src.load_order import get_load_order
    from src.visualizer import generate_plantuml, render_ascii_tree
except ModuleNotFoundError:
    from apk_parser import fetch_apkindex
    from graph_builder import (
        build_dependency_graph,
        parse_test_repository,
    )
    from load_order import get_load_order
    from visualizer import generate_plantuml, render_ascii_tree


def parse_arguments() -> argparse.Namespace:
    """Разобрать аргументы командной строки.

    Returns:
        argparse.Namespace: Разобранные аргументы.
    """
    parser = argparse.ArgumentParser(
        description="Визуализатор графа зависимостей Alpine apk."
    )
    parser.add_argument(
        "--package",
        required=True,
        type=str,
        help="Имя анализируемого пакета.",
    )
    parser.add_argument(
        "--repo",
        required=True,
        type=str,
        help="URL репозитория или путь к тестовому файлу.",
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Флаг режима работы с тестовым репозиторием.",
    )
    parser.add_argument(
        "--ascii-tree",
        action="store_true",
        help="Флаг вывода дерева зависимостей в формате ASCII.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Максимальная глубина анализа зависимостей.",
    )
    return parser.parse_args()


def validate_arguments(args: argparse.Namespace) -> None:
    """Проверить корректность переданных параметров.

    Args:
        args: Разобранные аргументы командной строки.

    Raises:
        ValueError: Если параметры содержат недопустимые значения.
    """
    if not args.package.strip():
        raise ValueError("Имя пакета не может быть пустым.")
    if not args.repo.strip():
        raise ValueError("URL или путь к репозиторию не может быть пустым.")
    if args.max_depth is not None and args.max_depth <= 0:
        raise ValueError("Глубина должна быть положительным числом.")


def main() -> None:
    """Основной сценарий выполнения приложения с наглядным выводом."""
    try:
        args = parse_arguments()
        validate_arguments(args)

        print("\n" + "=" * 60)
        print(" [ЭТАП 1] ПАРСИНГ И ВАЛИДАЦИЯ АРГУМЕНТОВ CLI")
        print("=" * 60)
        print(f" -> Целевой пакет : {args.package}")
        print(f" -> Источник данных: {args.repo}")
        print(f" -> Режим работы   : {'Тестовый (синтетический граф)' if args.test_mode else 'Основной (репозиторий Alpine)'}")
        print(f" -> Лимит глубины  : {args.max_depth if args.max_depth else 'Без ограничений'}")

        print("\n" + "=" * 60)
        print(" [ЭТАП 2] СБОР ДАННЫХ И ПАРСИНГ РЕПОЗИТОРИЯ")
        print("=" * 60)
        if args.test_mode:
            print(f"[*] Считывание тестового графа из файла...")
            packages = parse_test_repository(args.repo)
        else:
            print(f"[*] Загрузка и распаковка APKINDEX.tar.gz...")
            packages = fetch_apkindex(args.repo)

        print(f"[OK] База загружена. Всего пакетов в репозитории: {len(packages)}")

        target = args.package.strip()
        if target not in packages:
            print(f"\n[ОШИБКА] Пакет '{target}' отсутствует в репозитории!")
            sys.exit(1)

        direct_deps = packages.get(target, [])
        deps_preview = ", ".join(direct_deps) if direct_deps else "нет"
        print(f"[*] Прямые зависимости '{target}': {deps_preview}")

        print("\n" + "=" * 60)
        print(" [ЭТАП 3] ПОСТРОЕНИЕ ГРАФА (РЕКУРСИВНЫЙ BFS)")
        print("=" * 60)
        print(f"[*] Запуск послойного обхода от корня '{target}'...")
        graph, cycles = build_dependency_graph(
            target, packages, args.max_depth
        )
        print(f"[OK] Граф построен. Охвачено пакетов: {len(graph)}")
        for node, deps in graph.items():
            deps_str = ", ".join(deps) if deps else "(нет)"
            print(f"    - {node} -> {deps_str}")

        if cycles:
            print(f"\n[!] ВНИМАНИЕ: Найдено циклов: {len(cycles)}")
            for src, dst in sorted(cycles):
                print(f"    [ЦИКЛ] {src} -> {dst}")
        else:
            print("[OK] Циклических зависимостей не обнаружено.")

        print("\n" + "=" * 60)
        print(" [ЭТАП 4] ВЫЧИСЛЕНИЕ ПОРЯДКА УСТАНОВКИ (ТОПОЛОГИЧЕСКАЯ СОРТИРОВКА)")
        print("=" * 60)
        load_order = get_load_order(target, graph)
        print(f"[*] Очередность установки пакетов (от базовых к зависимым):")
        for idx, pkg in enumerate(load_order, start=1):
            arrow = " (целевой)" if pkg == target else ""
            print(f"    {idx}. {pkg}{arrow}")

        print("\n" + "=" * 60)
        print(" [ЭТАП 5] ГЕНЕРАЦИЯ ВИЗУАЛИЗАЦИИ")
        print("=" * 60)
        if args.ascii_tree:
            print("[*] Дерево зависимостей (ASCII):")
            print("----------------------------------------")
            tree_lines = render_ascii_tree(target, graph)
            print("\n".join(tree_lines))
            print("----------------------------------------\n")

        print("[*] Описание графа зависимостей (PlantUML):")
        print("----------------------------------------")
        plantuml_code = generate_plantuml(target, graph)
        print(plantuml_code)
        print("----------------------------------------\n")
        print("[ЗАВЕРШЕНО] Анализ успешно выполнен.\n")
    except Exception as error:
        print(f"\n[ОШИБКА ВЫПОЛНЕНИЯ] {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()