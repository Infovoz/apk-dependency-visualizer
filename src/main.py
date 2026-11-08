"""CLI entry point for dependency visualizer."""

import argparse
import sys


def parse_arguments() -> argparse.Namespace:
    """Parse and validate command line arguments.

    Returns:
        argparse.Namespace: Validated command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Alpine apk dependency visualizer."
    )
    parser.add_argument(
        "--package",
        required=True,
        type=str,
        help="Name of the package to analyze.",
    )
    parser.add_argument(
        "--repo",
        required=True,
        type=str,
        help="Repository URL or path to test repository file.",
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Flag to enable test repository mode.",
    )
    parser.add_argument(
        "--ascii-tree",
        action="store_true",
        help="Flag to enable ASCII tree output mode.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=None,
        help="Maximum depth of dependency analysis (integer > 0).",
    )
    return parser.parse_args()


def validate_arguments(args: argparse.Namespace) -> None:
    """Validate argument values and constraints.

    Args:
        args: Parsed arguments to validate.

    Raises:
        ValueError: If any argument value is invalid.
    """
    if not args.package.strip():
        raise ValueError("Package name cannot be empty.")
    if not args.repo.strip():
        raise ValueError("Repository path/URL cannot be empty.")
    if args.max_depth is not None and args.max_depth <= 0:
        raise ValueError("Max depth must be a positive integer.")


def print_configuration(args: argparse.Namespace) -> None:
    """Print configuration parameters in key-value format.

    Args:
        args: Validated arguments to display.
    """
    config = {
        "package": args.package,
        "repo": args.repo,
        "test_mode": args.test_mode,
        "ascii_tree": args.ascii_tree,
        "max_depth": args.max_depth,
    }
    for key, value in config.items():
        print(f"{key}: {value}")


def main() -> None:
    """Execute application workflow for stage 1."""
    try:
        args = parse_arguments()
        validate_arguments(args)
        print_configuration(args)
    except ValueError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()