"""
dbpykitpw Console - Centralized CLI interface with subcommands.

Main entry point for all dbpykitpw command-line tools.

Usage:
    dbpykitpw demo-publish [-o DIR] [-f] [-v]
    dbpykitpw dp [-o DIR] [-f] [-v]
    
    dbpykitpw template-generate NAME [-m DIR] [-r DIR] [-fk MODEL] [-f] [-v]
    dbpykitpw tg NAME [-m DIR] [-r DIR] [-fk MODEL] [-f] [-v]

Examples:
    dbpykitpw dp                           # Publish demo to current dir
    dbpykitpw demo-publish -o ./my_app     # Publish to specific dir
    
    dbpykitpw tg User                      # Generate User model/repo
    dbpykitpw template-generate User -fk Organization  # With FK
    dbpykitpw tg User -fk Org -fk Role -f -v  # Multiple FK, force, verbose
"""

import argparse
import sys
from typing import Optional, List

from .demo_publisher import DemoPublisher
from .template_generator import TemplateGenerator


def setup_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog='dbpykitpw',
        description='dbpykitpw - Database Python Kit with Peewee and Workflows',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  dbpykitpw demo-publish              Publish demo files to current directory
  dbpykitpw dp -o ./my_project        Publish demo to specific directory
  
  dbpykitpw template-generate User    Generate User model and repository
  dbpykitpw tg Product -fk User       Generate Product with FK to User
  dbpykitpw tg Order -fk User -fk Product  Generate with multiple FKs
        """
    )
    
    subparsers = parser.add_subparsers(
        title='commands',
        description='Available commands',
        dest='command',
        help='Command help'
    )
    
    # Demo Publish Command
    demo_parser = subparsers.add_parser(
        'demo-publish',
        aliases=['dp'],
        help='Publish demo files to project directory',
        description='Publish complete demo example files to your project'
    )
    demo_parser.add_argument(
        '-o', '--output',
        dest='output_dir',
        default=None,
        help='Output directory (default: current directory)'
    )
    demo_parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='Force overwrite existing files'
    )
    demo_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show verbose output'
    )
    demo_parser.set_defaults(func=handle_demo_publish)
    
    # Template Generate Command
    template_parser = subparsers.add_parser(
        'template-generate',
        aliases=['tg'],
        help='Generate model and repository templates',
        description='Generate boilerplate model and repository files for a new entity'
    )
    template_parser.add_argument(
        'name',
        help='Model name (e.g., User, Product, Order)'
    )
    template_parser.add_argument(
        '-m', '--models',
        dest='models_dir',
        default='./models',
        help='Models directory (default: ./models)'
    )
    template_parser.add_argument(
        '-r', '--repos',
        dest='repos_dir',
        default='./repositories',
        help='Repositories directory (default: ./repositories)'
    )
    template_parser.add_argument(
        '-fk', '--foreign-key',
        dest='foreign_keys',
        action='append',
        default=[],
        help='Foreign key model (can be used multiple times)'
    )
    template_parser.add_argument(
        '-f', '--force',
        action='store_true',
        help='Force overwrite existing files'
    )
    template_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show verbose output and next steps'
    )
    template_parser.set_defaults(func=handle_template_generate)
    
    return parser


def handle_demo_publish(args) -> int:
    """Handle demo-publish subcommand."""
    try:
        publisher = DemoPublisher(output_dir=args.output_dir)
        
        if not publisher.validate():
            return 1
        
        success = publisher.publish(force=args.force, verbose=args.verbose)
        return 0 if success else 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def handle_template_generate(args) -> int:
    """Handle template-generate subcommand."""
    try:
        from .util import print_result_table
        
        generator = TemplateGenerator(
            name=args.name,
            models_dir=args.models_dir,
            repos_dir=args.repos_dir,
            foreign_keys=args.foreign_keys,
            force=args.force
        )
        
        if not generator.validate():
            return 1
        
        result = generator.generate()
        print_result_table(result, verbose=args.verbose)
        return 0 if result['success'] else 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entry point for dbpykitpw console.
    
    Args:
        argv: Command-line arguments (default: sys.argv[1:])
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = setup_parser()
    args = parser.parse_args(argv)
    
    # If no command specified, show help
    if not hasattr(args, 'func'):
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
