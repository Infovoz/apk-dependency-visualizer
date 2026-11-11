"""Главный модуль CLI-приложения для визуализации графа зависимостей."""

import argparse
import sys

try:
    from src.apk_parser import fetch_and_parse_apkindex, parse_test_repo
    from src.graph_builder import build_dependency_graph
    from src.load_order import compute_load_order
    from src.visualizer import encode_plantuml, generate_plantuml, render_ascii_tree
except ModuleNotFoundError:
    from apk_parser import fetch_and_parse_apkindex, parse_test_repo
    from graph_builder import build_dependency_graph
    from load_order import compute_load_order
    from visualizer import encode_plantuml, generate_plantuml, render_ascii_tree


def parse_arguments() -> argparse.Namespace:
    """Создать парсер аргументов командной строки и вернуть распарсенные параметры."""
    parser = argparse.ArgumentParser(
        description="Инструмент визуализации графа зависимостей пакетов Alpine Linux (apk)."
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
        help="URL-адрес репозитория или путь к файлу тестового репозитория.",
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Режим работы с тестовым репозиторием (из локального файла).",
    )
    parser.add_argument(
        "--ascii-tree",
        action="store_true",
        help="Режим вывода зависимостей в формате ASCII-дерева.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Максимальная глубина анализа зависимостей.",
    )
    return parser.parse_args()


def validate_arguments(args: argparse.Namespace) -> None:
    """Проверить корректность переданных аргументов командной строки."""
    if not args.package or not args.package.strip():
        raise ValueError("Имя пакета не может быть пустым.")

    if not args.repo or not args.repo.strip():
        raise ValueError("URL или путь к репозиторию не может быть пустым.")

    if args.max_depth is not None and args.max_depth <= 0:
        raise ValueError("Глубина должна быть положительным числом.")


def main() -> None:
    """Точка входа в программу."""
    args = parse_arguments()

    try:
        validate_arguments(args)

        print("\n" + "=" * 60)
        print(" [ЭТАП 1] ПАРСИНГ И ВАЛИДАЦИЯ АРГУМЕНТОВ CLI")
        print("=" * 60)
        print(f" -> Целевой пакет : {args.package}")
        print(f" -> Источник данных: {args.repo}")
        print(
            f" -> Режим работы   : {'Тестовый (файл)' if args.test_mode else 'Основной (репозиторий Alpine)'}"
        )
        print(
            f" -> Лимит глубины  : {args.max_depth if args.max_depth is not None else 'Без ограничений'}"
        )

        target = args.package.strip()

        print("\n" + "=" * 60)
        print(" [ЭТАП 2] СБОР ДАННЫХ И ПАРСИНГ РЕПОЗИТОРИЯ")
        print("=" * 60)
        if args.test_mode:
            print("[*] Считывание тестового графа из файла...")
            repo_data = parse_test_repo(args.repo)
        else:
            print("[*] Загрузка и распаковка APKINDEX.tar.gz...")
            repo_data = fetch_and_parse_apkindex(args.repo)

        print(f"[OK] База загружена. Всего пакетов в репозитории: {len(repo_data)}")

        direct_deps = repo_data.get(target, [])
        deps_str = ", ".join(direct_deps) if direct_deps else "(нет)"
        print(f"[*] Прямые зависимости '{target}': {deps_str}")

        print("\n" + "=" * 60)
        print(" [ЭТАП 3] ПОСТРОЕНИЕ ГРАФА (РЕКУРСИВНЫЙ BFS)")
        print("=" * 60)
        print(f"[*] Запуск послойного обхода от корня '{target}'...")
        graph, cycles = build_dependency_graph(
            target,
            repo_data,
            max_depth=args.max_depth,
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

        print("\n" + "=" * 60)
        print(" [ЭТАП 4] ВЫЧИСЛЕНИЕ ПОРЯДКА УСТАНОВКИ (ТОПОЛОГИЧЕСКАЯ СОРТИРОВКА)")
        print("=" * 60)
        order = compute_load_order(target, graph)
        print("[*] Очередность установки пакетов (от базовых к зависимым):")
        for idx, pkg in enumerate(order, 1):
            flag = " (целевой)" if pkg == target else ""
            print(f"    {idx}. {pkg}{flag}")

        print("\n" + "=" * 60)
        print(" [ЭТАП 5] ГЕНЕРАЦИЯ ВИЗУАЛИЗАЦИИ")
        print("=" * 60)
        if args.ascii_tree:
            print("[*] Дерево зависимостей (ASCII):")
            print("----------------------------------------")
            tree_lines = render_ascii_tree(target, graph)
            print("\n".join(tree_lines))
            print("----------------------------------------\n")

        plantuml_code = generate_plantuml(target, graph)
        print("[*] Исходный код PlantUML:")
        print("----------------------------------------")
        print(plantuml_code)
        print("----------------------------------------")

        encoded_uml = encode_plantuml(plantuml_code)
        view_url = f"https://www.plantuml.com/plantuml/svg/{encoded_uml}"
        print(f"\n[*] Ссылка на готовую диаграмму (SVG):\n    {view_url}\n")

        print("[ЗАВЕРШЕНО] Анализ успешно выполнен.\n")

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