#!/usr/bin/env python3
"""
Script to detect code duplication in the UCAN project.

This script uses the 'pylint' similarity checker to identify duplicated code.
It can be run manually or as part of a pre-commit hook.
"""

import subprocess
import sys
from pathlib import Path


def run_pylint_similarity(min_similarity_percentage=60):
    """
    Run pylint's similarity checker to detect code duplication.

    Args:
        min_similarity_percentage: Minimum similarity percentage to report
            (default: 60)

    Returns:
        int: Return code (0 for success, non-zero for errors or duplications found)
    """
    # Get the project root directory
    project_root = Path(__file__).parent.parent.resolve()

    # Define the source directories to check
    source_dirs = [
        project_root / "ucan",
    ]

    # Build the command
    cmd = [
        "pylint",
        "--disable=all",
        "--enable=similarities",
        "--min-similarity-lines=5",
        "--ignore-comments=yes",
        "--ignore-docstrings=yes",
        "--ignore-imports=yes",
        f"--similarity-threshold={min_similarity_percentage}",
    ]

    # Add source directories to the command
    for source_dir in source_dirs:
        cmd.append(str(source_dir))

    # Run the command
    print(
        f"Checking for code duplication (similarity >= {min_similarity_percentage}%)..."
    )
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Check for errors
    if result.returncode != 0 and not result.stdout.strip():
        print(f"Error running pylint: {result.stderr}")
        return result.returncode

    # Process results
    if "Similar lines" in result.stdout:
        print("\n=== Potential Code Duplication Detected ===\n")
        print(result.stdout)

        print("\nRecommendations:")
        print("1. Review the duplicated code and consider refactoring")
        print("2. Extract common functionality into shared methods/classes")
        print("3. Use inheritance or composition to reuse code")
        return 1
    else:
        print("No significant code duplication detected.")
        return 0


def main():
    """Main entry point for the duplication checker."""
    # Check if pylint is installed
    try:
        subprocess.run(
            ["pylint", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except FileNotFoundError:
        print("Error: pylint is not installed. Install it with:")
        print("  pip install pylint")
        return 1

    # Get the similarity threshold from command line arguments
    min_similarity = 60  # Default threshold
    if len(sys.argv) > 1:
        try:
            min_similarity = int(sys.argv[1])
            if min_similarity < 0 or min_similarity > 100:
                raise ValueError("Threshold must be between 0 and 100")
        except ValueError as e:
            print(f"Error: Invalid similarity threshold: {e}")
            print(f"Using default threshold: {min_similarity}%")

    # Run the duplication checker
    return run_pylint_similarity(min_similarity)


if __name__ == "__main__":
    sys.exit(main())
