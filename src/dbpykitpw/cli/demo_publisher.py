"""
Demo Publisher CLI - Publish demo files to project root.

This module provides the 'pykitdbdemo' command-line tool that copies
the demo subpackage to a user's project root for template reference.
"""

import os
import shutil
import sys
import argparse
from pathlib import Path
from typing import Optional


class DemoPublisher:
    """
    Handles publishing demo files to a target project root.
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        Initialize the DemoPublisher.

        Args:
            output_dir: Target directory to publish demo files (default: current directory)
        """
        self.output_dir = Path(output_dir or os.getcwd())
        # Get the path to the demo package in the installed module
        self.demo_source = self._find_demo_source()

    def _find_demo_source(self) -> Optional[Path]:
        """
        Find the source demo package location.

        Returns:
            Path to the demo package or None if not found
        """
        # Try multiple possible locations for the demo package
        # demo_publisher.py structure:
        # src/dbpykitpw/cli/demo_publisher.py
        # We need to find: src/dbpykitpw/static/demo
        possible_locations = [
            # If running from source (src/dbpykitpw/cli/)
            Path(__file__).parent.parent / 'static' / 'demo',
            # If installed via pip in site-packages
            Path(__file__).parent.parent.parent / 'dbpykitpw' / 'static' / 'demo',
        ]

        for location in possible_locations:
            if location.exists() and location.is_dir():
                return location

        return None

    def validate(self) -> bool:
        """
        Validate that demo source exists and output directory is writable.

        Returns:
            True if validation passes, False otherwise
        """
        if not self.demo_source:
            print("✗ Error: Could not find demo package source")
            return False

        if not self.output_dir.exists():
            print(f"✗ Error: Output directory does not exist: {self.output_dir}")
            return False

        if not os.access(self.output_dir, os.W_OK):
            print(f"✗ Error: No write permissions for: {self.output_dir}")
            return False

        return True

    def publish(self, force: bool = False, verbose: bool = False) -> bool:
        """
        Publish demo files to the output directory.

        Args:
            force: Overwrite existing demo files
            verbose: Print detailed output

        Returns:
            True if successful, False otherwise
        """
        if not self.validate():
            return False

        target_demo_dir = self.output_dir / 'demo'

        # Check if demo already exists
        if target_demo_dir.exists():
            if not force:
                print(f"✗ Demo directory already exists: {target_demo_dir}")
                print("  Use --force to overwrite existing files")
                return False
            else:
                if verbose:
                    print(f"  Removing existing demo directory...")
                shutil.rmtree(target_demo_dir)

        # Copy the demo directory
        try:
            if verbose:
                print(f"  Copying demo package from {self.demo_source}")
                print(f"  to {target_demo_dir}")

            shutil.copytree(self.demo_source, target_demo_dir)

            print(f"✓ Demo files published successfully to: {target_demo_dir}")

            # Print information about the published files
            self._print_demo_info(target_demo_dir, verbose)

            return True

        except Exception as e:
            print(f"✗ Error during copying: {e}")
            return False

    def _print_demo_info(self, demo_dir: Path, verbose: bool = False):
        """
        Print information about published demo files.

        Args:
            demo_dir: Path to the published demo directory
            verbose: Print detailed information
        """
        print("\n  Published files:")

        try:
            for item in sorted(demo_dir.glob('*')):
                if item.is_file():
                    size = item.stat().st_size
                    print(f"    ✓ {item.name} ({size} bytes)")
                    if verbose:
                        print(f"      └─ {item}")

            if verbose:
                print(f"\n  Demo directory: {demo_dir}")
                print(f"  To run the demo: python -m demo.demo")

        except Exception as e:
            if verbose:
                print(f"  Error reading demo files: {e}")

    def __repr__(self) -> str:
        """String representation of DemoPublisher."""
        return (
            f"DemoPublisher(source={self.demo_source}, "
            f"output_dir={self.output_dir})"
        )

    def __str__(self) -> str:
        """User-friendly string representation."""
        demo_status = "Found" if self.demo_source else "Not found"
        return f"Demo Publisher ({demo_status})"


def main(argv: Optional[list] = None) -> int:
    """
    Main entry point for the pykitdbdemo command.

    Args:
        argv: Command-line arguments (default: sys.argv[1:])

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    parser = argparse.ArgumentParser(
        prog='pykitdbdemo',
        description='Publish dbpykitpw demo files to project root',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Publish demo to current directory
  pykitdbdemo

  # Publish demo to specific directory
  pykitdbdemo -o /path/to/project

  # Overwrite existing demo files
  pykitdbdemo --force

  # Print verbose output
  pykitdbdemo -v
        """,
    )

    parser.add_argument(
        '-o', '--output',
        dest='output_dir',
        default=None,
        help='Output directory for demo files (default: current directory)',
    )

    parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='Overwrite existing demo files',
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Print verbose output',
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0',
    )

    # Parse arguments
    args = parser.parse_args(argv)

    if args.verbose:
        print("=" * 80)
        print("  dbpykitpw Demo Publisher")
        print("=" * 80)
        print(f"\n  Output directory: {args.output_dir or os.getcwd()}")
        print(f"  Force overwrite: {args.force}")
        print()

    # Create publisher and publish
    publisher = DemoPublisher(output_dir=args.output_dir)

    if args.verbose:
        print(f"  Publisher: {repr(publisher)}\n")

    if publisher.publish(force=args.force, verbose=args.verbose):
        if args.verbose:
            print("\n  ✓ Demo publication completed successfully!")
        return 0
    else:
        if args.verbose:
            print("\n  ✗ Demo publication failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main())
