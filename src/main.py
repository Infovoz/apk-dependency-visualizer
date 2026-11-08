"""Точка входа CLI для визуализатора зависимостей."""

import argparse
import sys
from src.apk_parser import fetch_apkindex


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

        print(f"Загрузка репозитория: {args.repo}")
        packages = fetch_apkindex(args.repo)

        target = args.package.strip()
        if target not in packages:
            print(f"Пакет '{target}' не найден в репозитории.")
            sys.exit(1)

        direct_deps = packages[target]
        print(f"Прямые зависимости пакета '{target}':")
        for dep in direct_deps:
            print(f"  - {dep}")
    except Exception as error:
        print(f"Ошибка выполнения: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()