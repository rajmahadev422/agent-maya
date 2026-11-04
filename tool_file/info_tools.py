import json
import urllib.request
import urllib.parse
import os
from pathlib import Path
from config import PROJECT_DIR

def get_project_structure(directory: str = str(PROJECT_DIR), max_depth: int = 3, ignore_dirs: list = []) -> str:
    """Generate a Markdown tree representation of a project's files and folders.
    
    Args:
        directory: The root directory to scan (defaults to project directory).
        max_depth: Maximum folder depth to traverse (defaults to 3 to keep context concise).
        ignore_dirs: Optional list of folder names to ignore (defaults to common cache/build dirs based on project such as python project, node ect).
        
    Returns:
        A Markdown string containing a visual tree structure of the project.
    """
    if len(ignore_dirs) == 0:
        ignore_dirs = [".git", "node_modules", "__pycache__", "venv", ".venv", "dist", "build", ".idea", ".vscode"]
    else:
        ignore_dirs = [ignore_dirs]

    root_abs = os.path.abspath(directory)
    root_name = os.path.basename(root_abs) or root_abs
    
    lines = [f"# Project Structure (`{root_name}`)\n", "```text"]
    lines.append(f"{root_name}/")

    def build_tree(current_dir, prefix="", current_depth=1):
        if current_depth > max_depth:
            return
        
        try:
            entries = sorted(os.listdir(current_dir))
        except PermissionError:
            return

        # Filter out ignored directories and hidden files/folders if needed
        entries = [e for e in entries if e not in ignore_dirs and not e.startswith('.env')]
        
        for i, entry in enumerate(entries):
            path = os.path.join(current_dir, entry)
            is_dir = os.path.isdir(path)
            
            # Determine tree branch characters
            is_last = (i == len(entries) - 1)
            pointer = "└── " if is_last else "├── "
            
            lines.append(f"{prefix}{pointer}{entry}{'/' if is_dir else ''}")
            
            if is_dir:
                extension = "    " if is_last else "│   "
                build_tree(path, prefix + extension, current_depth + 1)

    build_tree(directory, prefix="", current_depth=1)
    lines.append("```")
    
    return "\n".join(lines)
