#!/usr/bin/env python3
"""
Template Generator - Create model and repository templates.

This CLI tool generates template model and repository files for use with dbpykitpw.
It creates Ready-to-use templates with all necessary imports and structure.

Usage:
    python template_generator.py User --models ./models --repos ./repositories
    python template_generator.py Product
    python template_generator.py Post -m ./app/models -r ./app/repos
"""

import argparse
import os
import sys
from pathlib import Path
from textwrap import dedent

# Import CLI utilities
try:
    from dbpykitpw.cli.util import (
        print_header, print_section, print_success, print_error,
        print_result_table, print_file_info, confirm_override
    )
except ImportError:
    # Fallback for standalone usage
    from util import (
        print_header, print_section, print_success, print_error,
        print_result_table, print_file_info, confirm_override
    )



class TemplateGenerator:
    """Generate model and repository template files."""
    
    def __init__(self, name, models_dir="./models", repos_dir="./repositories", foreign_keys=None, force=False):
        """Initialize template generator.
        
        Args:
            name: Model name (e.g., "User", "Product")
            models_dir: Directory for model files
            repos_dir: Directory for repository files
            foreign_keys: List of foreign key references (e.g., ["User", "Category"])
            force: Force overwrite if files exist
        """
        self.name = name
        self.class_name = self._to_class_name(name)
        self.snake_case = self._to_snake_case(name)
        self.models_dir = Path(models_dir)
        self.repos_dir = Path(repos_dir)
        self.repo_class_name = f"{self.class_name}Repository"
        self.foreign_keys = foreign_keys or []
        self.force = force
    
    @staticmethod
    def _to_class_name(name):
        """Convert name to PascalCase class name.
        
        Examples:
            user → User
            product_item → ProductItem
            productItem → ProductItem
        """
        # Handle snake_case
        if "_" in name:
            parts = name.split("_")
            return "".join(p.capitalize() for p in parts)
        # Handle camelCase - just capitalize first letter
        return name[0].upper() + name[1:] if name else ""
    
    @staticmethod
    def _to_snake_case(name):
        """Convert name to snake_case.
        
        Examples:
            User → user
            ProductItem → product_item
            product → product
        """
        result = []
        for i, char in enumerate(name):
            if char.isupper() and i > 0:
                result.append("_")
                result.append(char.lower())
            else:
                result.append(char.lower())
        return "".join(result)
    
    def _generate_model_template(self):
        """Generate model file content from template."""
        # Load template
        template_path = Path(__file__).parent.parent / "static" / "templates" / "model_template.py"
        template_content = template_path.read_text()
        
        # Build ForeignKey import if needed
        fk_import = ""
        if self.foreign_keys:
            fk_import = ", ForeignKey"
        
        # Build foreign key field declarations
        fk_fields = ""
        if self.foreign_keys:
            fk_fields = "\n    # Foreign key relationships:\n"
            for fk in self.foreign_keys:
                fk_class = self._to_class_name(fk)
                fk_snake = self._to_snake_case(fk)
                fk_fields += f"    # {fk_snake} = ForeignKey({fk_class}, backref='{self.snake_case}s')\n"
            fk_fields += "\n    "
        
        # Build imports for FK models if needed
        fk_imports = ""
        if self.foreign_keys:
            fk_modules = ", ".join([self._to_snake_case(fk) for fk in self.foreign_keys])
            fk_imports = f"# from models import {fk_modules}\n"
        
        # Replace placeholders
        content = template_content
        content = content.replace("{{MODEL_CLASS}}", self.class_name)
        content = content.replace("{{SNAKE_CASE}}", self.snake_case)
        content = content.replace("{{FK_IMPORT_FK}}", fk_import)
        content = content.replace("{{FK_FIELDS}}", fk_fields)
        content = content.replace("{{FK_IMPORTS}}", fk_imports)
        
        return content.strip()
    
    
    def _generate_repository_template(self):
        """Generate repository file content from template."""
        # Load template
        template_path = Path(__file__).parent.parent / "static" / "templates" / "repository_template.py"
        template_content = template_path.read_text()
        
        # Build import statement for foreign key models if needed
        fk_imports_repo = ""
        if self.foreign_keys:
            fk_modules = ", ".join([self._to_snake_case(fk) for fk in self.foreign_keys])
            fk_imports_repo = f"\n# from models import {fk_modules}"
        
        # Build foreign key query examples
        fk_examples = ""
        if self.foreign_keys:
            fk_examples = "\n    # Example queries with foreign keys:\n"
            for fk in self.foreign_keys:
                fk_class = self._to_class_name(fk)
                fk_snake = self._to_snake_case(fk)
                fk_examples += f"    # def get_by_{fk_snake}(self, {fk_snake}_id):\n"
                fk_examples += f"    #     \"\"\"Get all {{MODEL_CLASS}} for a specific {fk_class}.\"\"\"\n"
                fk_examples += f"    #     query = {{MODEL_CLASS}}.select().where({{MODEL_CLASS}}.{fk_snake} == {fk_snake}_id)\n"
                fk_examples += f"    #     return list(query)\n    #\n"
        
        # Replace placeholders
        content = template_content
        content = content.replace("{{MODEL_CLASS}}", self.class_name)
        content = content.replace("{{REPO_CLASS}}", self.repo_class_name)
        content = content.replace("{{SNAKE_CASE}}", self.snake_case)
        content = content.replace("{{FK_IMPORTS_REPO}}", fk_imports_repo)
        content = content.replace("{{FK_EXAMPLES}}", fk_examples)
        
        return content.strip()
    
    
    def validate(self):
        """Validate inputs and check for conflicts.
        
        Returns:
            tuple: (is_valid, error_messages)
        """
        errors = []
        
        # Check if name is valid
        if not self.name or len(self.name) < 1:
            errors.append("Model name is required")
        
        if not self.class_name[0].isupper():
            errors.append(f"Model name must start with uppercase letter (got: {self.name})")
        
        # Check if files already exist (only if not forcing)
        if not self.force:
            model_file = self.models_dir / f"{self.snake_case}.py"
            repo_file = self.repos_dir / f"{self.snake_case}_repo.py"
            
            if model_file.exists():
                errors.append(f"Model file already exists: {model_file} (use -f to override)")
            
            if repo_file.exists():
                errors.append(f"Repository file already exists: {repo_file} (use -f to override)")
        
        return len(errors) == 0, errors
    
    def create_directories(self):
        """Create model and repository directories if they don't exist."""
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.repos_dir.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py files
        models_init = self.models_dir / "__init__.py"
        if not models_init.exists():
            models_init.write_text("# Models package\n")
        
        repos_init = self.repos_dir / "__init__.py"
        if not repos_init.exists():
            repos_init.write_text("# Repositories package\n")
    
    def generate(self):
        """Generate model and repository files.
        
        Returns:
            dict: Generation result with success status and file paths
        """
        # Validate
        is_valid, errors = self.validate()
        if not is_valid:
            return {
                "success": False,
                "errors": errors
            }
        
        # Create directories
        self.create_directories()
        
        # Generate model file
        model_file = self.models_dir / f"{self.snake_case}.py"
        model_content = self._generate_model_template()
        model_file.write_text(model_content + "\n")
        
        # Generate repository file
        repo_file = self.repos_dir / f"{self.snake_case}_repo.py"
        repo_content = self._generate_repository_template()
        repo_file.write_text(repo_content + "\n")
        
        return {
            "success": True,
            "model_file": str(model_file),
            "repository_file": str(repo_file),
            "model_class": self.class_name,
            "repository_class": self.repo_class_name,
            "foreign_keys": self.foreign_keys,
            "message": f"✓ Templates created for {self.class_name}"
        }



def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Generate model and repository template files for dbpykitpw",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""
            Examples:
              %(prog)s User
              %(prog)s Product --models ./app/models --repos ./app/repos
              %(prog)s BlogPost -m ./src/models -r ./src/repositories -v
              %(prog)s Comment -fk User -fk Post
              %(prog)s OrderItem -fk Order -fk Product
        """)
    )
    
    parser.add_argument(
        "name",
        help="Model name (e.g., User, Product, BlogPost)"
    )
    
    parser.add_argument(
        "-m", "--models",
        dest="models_dir",
        default="./models",
        help="Models directory (default: ./models)"
    )
    
    parser.add_argument(
        "-r", "--repos", "--repositories",
        dest="repos_dir",
        default="./repositories",
        help="Repositories directory (default: ./repositories)"
    )
    
    parser.add_argument(
        "-fk", "--foreign-key",
        dest="foreign_keys",
        action="append",
        default=[],
        help="Foreign key reference(s) (e.g., -fk User -fk Category)"
    )
    
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force overwrite existing files"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output with next steps"
    )
    
    args = parser.parse_args()
    
    # Generate templates
    generator = TemplateGenerator(
        name=args.name,
        models_dir=args.models_dir,
        repos_dir=args.repos_dir,
        foreign_keys=args.foreign_keys,
        force=args.force
    )
    
    result = generator.generate()
    print_result_table(result, verbose=args.verbose)
    
    # Return exit code
    return 0 if result["success"] else 1




if __name__ == "__main__":
    sys.exit(main())
