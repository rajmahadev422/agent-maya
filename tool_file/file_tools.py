
import os
from pathlib import Path


def get_safe_path(file_path: str, directory: str = "./") -> Path:
    """Resolve a path and prevent access outside the working directory."""

    base_dir = Path(directory or "./").resolve()
    target = Path(file_path)

    if not target.is_absolute():
        target = base_dir / target

    target = target.resolve()

    if not target.is_relative_to(base_dir):
        raise PermissionError("Access denied: Outside working directory.")

    return target


def read_file(file_path: str, directory: str = "./") -> str:
    """Read file content."""

    try:
        path = get_safe_path(file_path, directory)

        if not path.exists():
            return f"Error: File not found: {file_path}"

        if not path.is_file():
            return "Error: Path is not a file."

        return path.read_text(encoding="utf-8") or "File is empty."

    except UnicodeDecodeError:
        return "Error: Cannot read binary file as text."
    except Exception as e:
        return f"Read error: {e}"


def write_file(
    file_path: str,
    content: str,
    directory: str = "./"
) -> str:
    """Create a new file or overwrite an existing file."""

    try:
        path = get_safe_path(file_path, directory)

        if path.exists() and path.is_dir():
            return "Error: Path is a directory."

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

        return f"File written successfully: {path}"

    except Exception as e:
        return f"Write error: {e}"


def update_file(
    file_path: str,
    old_text: str,
    new_text: str,
    directory: str = "./",
    replace_all: bool = False
) -> str:
    """Replace specific text inside an existing file."""

    try:
        path = get_safe_path(file_path, directory)

        if not path.is_file():
            return f"Error: File not found: {file_path}"

        content = path.read_text(encoding="utf-8")

        if not old_text:
            return "Error: old_text cannot be empty."

        if old_text not in content:
            return "Error: Target text not found in file."

        count = content.count(old_text)

        if not replace_all and count > 1:
            return (
                f"Error: Text found {count} times. "
                "Provide more specific old_text or enable replace_all."
            )

        if replace_all:
            updated = content.replace(old_text, new_text)
        else:
            updated = content.replace(old_text, new_text, 1)

        path.write_text(updated, encoding="utf-8")

        return f"File updated successfully. Replacements: {count if replace_all else 1}"

    except Exception as e:
        return f"Update error: {e}"


def delete_file(file_path: str, directory: str = "./") -> str:
    """Delete an existing file."""

    try:
        path = get_safe_path(file_path, directory)

        if not path.exists():
            return f"Error: File not found: {file_path}"

        if not path.is_file():
            return "Error: Cannot delete a directory using this tool."

        path.unlink()

        return f"File deleted successfully: {file_path}"

    except Exception as e:
        return f"Delete error: {e}"


def list_files(
    directory: str = "./",
    recursive: bool = False
) -> str:
    """List files and folders inside a directory."""

    try:
        path = Path(directory or "./").resolve()

        if not path.is_dir():
            return "Error: Directory does not exist."

        entries = []

        iterator = path.rglob("*") if recursive else path.iterdir()

        for item in iterator:
            # Skip symlinks to avoid exposing paths outside the directory.
            if item.is_symlink():
                continue

            relative = item.relative_to(path)

            if item.is_dir():
                entries.append(f"[DIR]  {relative}")
            elif item.is_file():
                entries.append(f"[FILE] {relative}")

        if not entries:
            return "Directory is empty."

        return "\n".join(sorted(entries))

    except Exception as e:
        return f"List error: {e}"
