import os
from pathlib import Path
from config import PROJECT_DIR

def list_directory(directory: str = str(PROJECT_DIR), recursive: bool = True) -> str:
  """List files and folders in a specified directory to understand project structure.

  Args:
      directory_path: The target directory path to list. Defaults to './'.
      recursive: If true, lists contents recursively (up to a safe depth).

  Returns:
      A formatted string listing directories and files.
  """
  try:
    target_dir = Path(directory).resolve()

    if not target_dir.is_dir():
      return f"Error: Directory not found or is not a directory: {directory}"

    entries = []
    not_include = ["node_modules", "venv", ".venv", "__pycache__"]
    if recursive:
      for path in target_dir.rglob("*"):
        # Skip hidden files/folders like .git or node_modules to save context
        if any(
            part.startswith(".") or part in not_include
            for part in path.parts
        ):
          continue
        rel_path = path.relative_to(target_dir)
        prefix = "[DIR]  " if path.is_dir() else "[FILE] "
        entries.append(f"{prefix}{rel_path}")
    else:
      for item in sorted(target_dir.iterdir()):
        if item.name.startswith(".") or item.name == "node_modules":
          continue
        prefix = "[DIR]  " if item.is_dir() else "[FILE] "
        entries.append(f"{prefix}{item.name}")

    if not entries:
      return "Directory is empty."

    return f"Contents of {target_dir}:\n" + "\n".join(entries[:100])

  except Exception as e:
     return f"Error listing directory: {str(e)}"

