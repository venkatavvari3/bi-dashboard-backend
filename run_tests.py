#!/usr/bin/env python3
"""
Test runner script for BI Dashboard Backend
Provides convenient commands for running different types of tests
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_command(command: list, description: str):
    """Run a command and handle errors."""
    print(f"\n🧪 {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run(command, check=True, capture_output=False)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False


def install_test_dependencies():
    """Install test dependencies."""
    return run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        "Installing test dependencies"
    )


def run_unit_tests():
    """Run unit tests only."""
    return run_command(
        [sys.executable, "-m", "pytest", "tests/unit/", "-v", "--tb=short"],
        "Running unit tests"
    )


def run_integration_tests():
    """Run integration tests only."""
    return run_command(
        [sys.executable, "-m", "pytest", "tests/integration/", "-v", "--tb=short"],
        "Running integration tests"
    )


def run_all_tests():
    """Run all tests."""
    return run_command(
        [sys.executable, "-m", "pytest", "tests/", "-v"],
        "Running all tests"
    )


def run_tests_with_coverage():
    """Run tests with coverage report."""
    return run_command(
        [sys.executable, "-m", "pytest", "tests/", "--cov=app", "--cov-report=term-missing", "--cov-report=html"],
        "Running tests with coverage"
    )


def run_specific_test(test_path: str):
    """Run a specific test file or test function."""
    return run_command(
        [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"],
        f"Running specific test: {test_path}"
    )


def lint_code():
    """Run code linting (if flake8 is available)."""
    try:
        return run_command(
            [sys.executable, "-m", "flake8", "app/", "tests/", "--max-line-length=100"],
            "Running code linting"
        )
    except FileNotFoundError:
        print("📝 flake8 not installed, skipping linting")
        return True


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="BI Dashboard Backend Test Runner")
    parser.add_argument(
        "command",
        choices=["install", "unit", "integration", "all", "coverage", "lint", "specific"],
        help="Test command to run"
    )
    parser.add_argument(
        "--test-path",
        help="Specific test path (for 'specific' command)"
    )
    
    args = parser.parse_args()
    
    print("🚀 BI Dashboard Backend Test Runner")
    print("=" * 50)
    
    success = True
    
    if args.command == "install":
        success = install_test_dependencies()
    
    elif args.command == "unit":
        success = run_unit_tests()
    
    elif args.command == "integration":
        success = run_integration_tests()
    
    elif args.command == "all":
        success = run_all_tests()
    
    elif args.command == "coverage":
        success = run_tests_with_coverage()
        if success:
            print("\n📊 Coverage report generated in htmlcov/index.html")
    
    elif args.command == "lint":
        success = lint_code()
    
    elif args.command == "specific":
        if not args.test_path:
            print("❌ --test-path required for 'specific' command")
            sys.exit(1)
        success = run_specific_test(args.test_path)
    
    if success:
        print(f"\n🎉 {args.command.title()} command completed successfully!")
        sys.exit(0)
    else:
        print(f"\n💥 {args.command.title()} command failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
