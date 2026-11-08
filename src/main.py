"""Точка входа CLI для визуализатора зависимостей."""

import argparse
import sys

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
    """Основной сценарий выполнения приложения."""
    try:
        args = parse_arguments()
        validate_arguments(args)

        if args.test_mode:
            print(f"Режим тестирования. Чтение графа из: {args.repo}")
            packages = parse_test_repository(args.repo)
        else:
            print(f"Загрузка репозитория Alpine: {args.repo}")
            packages = fetch_apkindex(args.repo)

        target = args.package.strip()
        if target not in packages:
            print(f"Пакет '{target}' не найден в репозитории.")
            sys.exit(1)

        graph, cycles = build_dependency_graph(
            target, packages, args.max_depth
        )

        load_order = get_load_order(target, graph)
        print(f"\nПорядок загрузки зависимостей для '{target}':")
        for idx, pkg in enumerate(load_order, start=1):
            print(f"  {idx}. {pkg}")

        if cycles:
            print("\nОбнаружены циклические зависимости:")
            for src, dst in sorted(cycles):
                print(f"  {src} -> {dst} (цикл)")

        if args.ascii_tree:
            print(f"\nASCII-дерево зависимостей:")
            tree_lines = render_ascii_tree(target, graph)
            print("\n".join(tree_lines))

        print(f"\nОписание графа зависимостей (PlantUML):")
        print("----------------------------------------")
        plantuml_code = generate_plantuml(target, graph)
        print(plantuml_code)
        print("----------------------------------------")

    except Exception as error:
        print(f"Ошибка выполнения: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()