import os
import sys
from pathlib import Path

def should_ignore(path, name):
    """
    Check if a file or directory should be ignored based on common Django patterns.
    """
    ignore_patterns = {
        # Cache directories
        '__pycache__',
        '.pytest_cache',
        '.mypy_cache',
        '.coverage',
        'htmlcov',
        
        # Environment directories
        'venv',
        'env',
        '.env',
        'virtualenv',
        
        # Version control
        '.git',
        '.svn',
        '.hg',
        
        # IDE/Editor files
        '.vscode',
        '.idea',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.DS_Store',
        'Thumbs.db',
        
        # Django specific
        'static_root',
        'media_root',
        'staticfiles',
        
        # Database files
        'db.sqlite3',
        '*.db',
        
        # Log files
        '*.log',
        'logs',
        
        # Build/Distribution
        'build',
        'dist',
        '*.egg-info',
        
        # Node modules (if using frontend tools)
        'node_modules',
        
        # Jupyter notebooks checkpoints
        '.ipynb_checkpoints',
    }
    
    # Check if the name matches any ignore pattern
    for pattern in ignore_patterns:
        if pattern.startswith('*') and name.endswith(pattern[1:]):
            return True
        elif name == pattern:
            return True
    
    # Check if it's a hidden file/directory (starts with .)
    if name.startswith('.') and name not in {'.gitignore', '.env.example'}:
        return True
    
    return False

def print_tree(directory, prefix="", is_last=True, max_depth=None, current_depth=0):
    """
    Print the directory tree structure.
    
    Args:
        directory: Path to the directory
        prefix: Current line prefix for tree formatting
        is_last: Whether this is the last item in its parent directory
        max_depth: Maximum depth to traverse (None for unlimited)
        current_depth: Current depth level
    """
    if max_depth is not None and current_depth >= max_depth:
        return
    
    directory = Path(directory)
    if not directory.exists():
        print(f"Directory '{directory}' does not exist.")
        return
    
    # Get all items in the directory, filtered by our ignore rules
    try:
        items = [item for item in directory.iterdir() 
                if not should_ignore(directory, item.name)]
        items.sort(key=lambda x: (x.is_file(), x.name.lower()))
    except PermissionError:
        print(f"{prefix}[Permission Denied]")
        return
    
    for i, item in enumerate(items):
        is_last_item = i == len(items) - 1
        
        # Create the tree branch
        if is_last_item:
            current_prefix = prefix + "└── "
            next_prefix = prefix + "    "
        else:
            current_prefix = prefix + "├── "
            next_prefix = prefix + "│   "
        
        # Print the current item
        if item.is_dir():
            print(f"{current_prefix}{item.name}/")
            # Recursively print subdirectory
            print_tree(item, next_prefix, is_last_item, max_depth, current_depth + 1)
        else:
            print(f"{current_prefix}{item.name}")

def main():
    """
    Main function to run the tree structure printer.
    """
    # Get the project directory (default to current directory)
    if len(sys.argv) > 1:
        project_dir = sys.argv[1]
    else:
        project_dir = "."
    
    # Get max depth if provided
    max_depth = None
    if len(sys.argv) > 2:
        try:
            max_depth = int(sys.argv[2])
        except ValueError:
            print("Warning: Invalid max depth provided. Using unlimited depth.")
    
    project_path = Path(project_dir).resolve()
    
    # Check if it's likely a Django project
    django_indicators = ['manage.py', 'settings.py']
    has_django_files = any(
        list(project_path.glob(f"**/{indicator}")) 
        for indicator in django_indicators
    )
    
    if not has_django_files:
        print("Warning: This doesn't appear to be a Django project directory.")
        print("(No manage.py or settings.py found)")
        print()
    
    print(f"Django Project Tree Structure: {project_path.name}")
    print("=" * 50)
    print_tree(project_path, max_depth=max_depth)
    
    # Print some statistics
    print("\n" + "=" * 50)
    total_files = sum(1 for _ in project_path.rglob("*") if _.is_file() and not should_ignore(_.parent, _.name))
    total_dirs = sum(1 for _ in project_path.rglob("*") if _.is_dir() and not should_ignore(_.parent, _.name))
    print(f"Total files: {total_files}")
    print(f"Total directories: {total_dirs}")

if __name__ == "__main__":
    main()
