"""Unit tests for Stage 1 CLI configuration."""

import argparse
import unittest

from src.main import validate_arguments


class TestCliValidation(unittest.TestCase):
    """Test validation of CLI arguments."""

    def test_valid_arguments(self) -> None:
        """Test validation passes with correct parameters."""
        args = argparse.Namespace(
            package="curl",
            repo="https://example.com/repo",
            test_mode=False,
            ascii_tree=True,
            max_depth=3,
        )
        try:
            validate_arguments(args)
        except ValueError:
            self.fail("validate_arguments raised ValueError unexpectedly.")

    def test_empty_package_raises_error(self) -> None:
        """Test error raised when package name is blank."""
        args = argparse.Namespace(
            package="   ",
            repo="https://example.com/repo",
            test_mode=False,
            ascii_tree=False,
            max_depth=1,
        )
        with self.assertRaises(ValueError):
            validate_arguments(args)

    def test_negative_depth_raises_error(self) -> None:
        """Test error raised when max depth is not positive."""
        args = argparse.Namespace(
            package="curl",
            repo="test_repo.txt",
            test_mode=True,
            ascii_tree=False,
            max_depth=0,
        )
        with self.assertRaises(ValueError):
            validate_arguments(args)


if __name__ == "__main__":
    unittest.main()