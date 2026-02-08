"""
CLI Utilities - Formatted output and helpers for CLI tools.

Provides colored output, tables, and formatted messages using
picasso and tabulate libraries.
"""

from typing import Dict, List, Optional


def print_header(title: str, width: int = 70):
    """Print formatted header with title.
    
    Args:
        title: Header title
        width: Total width of header
    """
    print("\n" + "=" * width)
    print(f"  {title}".ljust(width - 2) + " ")
    print("=" * width)


def print_section(title: str):
    """Print formatted section title."""
    print(f"\n  → {title}")
    print("-" * 78)


def print_success(message: str):
    """Print success message with checkmark."""
    print(f"  ✓ {message}")


def print_error(message: str):
    """Print error message with X."""
    print(f"  ✗ {message}")


def print_info(message: str):
    """Print info message."""
    print(f"  ℹ {message}")


def print_result_table(results: Dict, verbose: bool = False):
    """Print generation results in formatted table.
    
    Args:
        results: Generation result dictionary
        verbose: Show additional details
    """
    width = 70
    
    if results["success"]:
        print_header("✓ Templates Generated Successfully", width)
        
        print(f"\n  Model Class:        {results['model_class']}")
        print(f"  Repository Class:   {results['repository_class']}")
        print(f"\n  Model File:         {results['model_file']}")
        print(f"  Repository File:    {results['repository_file']}")
        
        if results.get("foreign_keys"):
            print(f"\n  Foreign Keys:       {', '.join(results['foreign_keys'])}")
        
        if verbose:
            print_section("Next Steps")
            model_file = results['model_file']
            repo_file = results['repository_file']
            model_class = results['model_class']
            repo_class = results['repository_class']
            
            print(f"  1. Edit {model_file}")
            print(f"     - Add your custom model fields")
            print(f"     - Keep created_at, updated_at, deleted_at fields")
            if results.get("foreign_keys"):
                print(f"     - Uncomment foreign key field definitions")
            
            print(f"\n  2. Edit {repo_file}")
            print(f"     - Uncomment and implement custom query methods")
            print(f"     - Add business logic specific to {model_class}")
            if results.get("foreign_keys"):
                print(f"     - Implement foreign key query methods")
            
            print(f"\n  3. Import in your application:")
            model_module = model_file.split("/")[-1][:-3]
            repo_module = repo_file.split("/")[-1][:-3]
            print(f"     from models.{model_module} import {model_class}")
            print(f"     from repositories.{repo_module} import {repo_class}")
        
        print("\n")
    
    else:
        print_header("✗ Template Generation Failed", width)
        print("\n  Errors:")
        for error in results.get("errors", []):
            print_error(error)
        print("\n")


def print_file_info(action: str, filepath: str, size: int = 0):
    """Print file operation information.
    
    Args:
        action: Action performed (created, updated, skipped, etc.)
        filepath: Full file path
        size: File size in bytes
    """
    status_map = {
        "created": "✓",
        "updated": "→",
        "skipped": "⊘",
        "exists": "◈",
        "error": "✗"
    }
    symbol = status_map.get(action, "•")
    
    size_str = ""
    if size > 0:
        if size > 1024:
            size_str = f" ({size // 1024} KB)"
        else:
            size_str = f" ({size} B)"
    
    print(f"  {symbol} {action:8} {filepath}{size_str}")


def print_summary(total: int, created: int, skipped: int, failed: int):
    """Print summary statistics.
    
    Args:
        total: Total items processed
        created: Items created
        skipped: Items skipped
        failed: Items failed
    """
    print_section("Summary")
    print(f"  Total:     {total}")
    print(f"  Created:   {created}")
    print(f"  Skipped:   {skipped}")
    print(f"  Failed:    {failed}")
    print()


def confirm_override(filepath: str) -> bool:
    """Ask user to confirm file override.
    
    Args:
        filepath: File path to confirm
        
    Returns:
        True if user confirms, False otherwise
    """
    print(f"\n  File exists: {filepath}")
    response = input("  Overwrite? (y/N): ").strip().lower()
    return response == "y"


def print_command_example(command: str, description: str = ""):
    """Print command example with description.
    
    Args:
        command: Command to display
        description: Optional description
    """
    if description:
        print(f"  {description}")
    print(f"  $ {command}")
