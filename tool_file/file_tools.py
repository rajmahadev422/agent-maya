import os
import json
from pathlib import Path
from config import PROJECT_DIR

directory = PROJECT_DIR

def search_files(query: str, extension: str = "") -> str:
    """Search for files in the current directory matching a text query or extension.
    
    Args:
        query: The search term to look for in file names or contents.
        extension: Optional file extension filter (e.g., '.txt', '.py', '.md').
        
    Returns:
        A JSON string containing a list of matched files with their paths and snippets.
    """
    matches = []
    
    for root, _, files in os.walk(directory):
        for file in files:
            if extension != "" and not file.endswith(extension):
                continue
                
            file_path = os.path.join(root, file)
            
            # Match by file name
            if query.lower() in file.lower():
                matches.append({
                    "path": file_path,
                    "match_type": "filename",
                    "snippet": f"Matched file name: {file}"
                })
                continue
                
            # Match inside file contents
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if query.lower() in content.lower():
                        idx = content.lower().find(query.lower())
                        start = max(0, idx - 60)
                        end = min(len(content), idx + 100)
                        snippet = "..." + content[start:end].replace("\n", " ") + "..."
                        
                        matches.append({
                            "path": file_path,
                            "match_type": "content",
                            "snippet": snippet
                        })
            except Exception:
                continue

    return json.dumps(matches[:10])


def read_file(file_path: str) -> str:
    """Read the contents of a file.
    
    Args:
        file_path: Targeted file absolute path to read that file content.
        
    Returns:
        The file content as a string, or an error message if failed.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"


def write_file(file_path: str, content: str) -> str:
    """Write content to a file (creates the file or overwrites it if it exists).
    
    Args:
        file_path: Targeted file absolute path to write in that file.
        content: The text content to write into the file.
        
    Returns:
        A success or error message.
    """
    try:
        directory = os.path.dirname(os.path.abspath(file_path))
        if directory:
            os.makedirs(directory, exist_ok=True)
            
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing file: {str(e)}"



def delete_file(file_path: str) -> str:
    """Delete a file from the file system.
    
    Args:
        file_path: Targeted file absolute path to delete that file.
        
    Returns:
        A success or error message.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return f"Successfully deleted {file_path}"
        else:
            return f"Error: File {file_path} does not exist."
    except Exception as e:
        return f"Error deleting file: {str(e)}"
    


def get_safe_path(file_path: str, directory: str = "./") -> Path:
    """Resolve file path inside the working directory."""

    base = Path(directory or "./").resolve()
    target = Path(file_path)

    if not target.is_absolute():
        target = base / target

    target = target.resolve()

    if not target.is_relative_to(base):
        raise PermissionError("Access denied: Outside working directory.")

    return target


def update_file(
    file_path: str,
    content: str,
    directory: str = "./"
) -> str:
    """
    Replace the entire content of an existing file.

    Args:
        file_path: Targeted file absolute path.
        content: New complete file content.
        directory: Project working directory.

    Returns:
        Update status.
    """

    try:
        path = get_safe_path(file_path, directory)

        if not path.is_file():
            return f"Error: File not found: {file_path}"

        path.write_text(content, encoding="utf-8")

        return f"File completely updated: {file_path}"

    except Exception as e:
        return f"Update error: {e}"


def insert_file_text(
    file_path: str,
    text: str,
    position: str,
    directory: str = "./",
    reference_text: str = ""
) -> str:
    """
    Insert text at the beginning, end or a specific location.

    Args:
        file_path: Targeted file absolute path.
        text: Text to insert.
        position: beginning, end or after/before.
        directory: Project working directory.
        reference_text: Existing text used as insertion anchor.

    Returns:
        Insertion status.
    """

    try:
        path = get_safe_path(file_path, directory)

        if not path.is_file():
            return f"Error: File not found: {file_path}"

        content = path.read_text(encoding="utf-8")

        if position == "beginning":
            updated = text + content

        elif position == "end":
            updated = content + text

        elif position in ("before", "after"):
            if not reference_text:
                return "Error: reference_text is required."

            count = content.count(reference_text)

            if count == 0:
                return "Error: Reference text not found."

            if count > 1:
                return "Error: Reference text is ambiguous. Use unique text."

            index = content.index(reference_text)

            if position == "before":
                updated = (
                    content[:index] + text + content[index:]
                )
            else:
                end_index = index + len(reference_text)
                updated = (
                    content[:end_index] + text + content[end_index:]
                )

        else:
            return "Error: position must be beginning, end, before or after."

        path.write_text(updated, encoding="utf-8")

        return f"Text inserted successfully at {position}: {file_path}"

    except Exception as e:
        return f"Insert error: {e}"


def replace_file_text(
    file_path: str,
    old_text: str,
    new_text: str,
    directory: str = "./",
    replace_all: bool = False
) -> str:
    """
    Replace specific text inside an existing file.

    Args:
        file_path: Targeted file absolute path.
        old_text: Existing text to find.
        new_text: Replacement text.
        directory: Project working directory.
        replace_all: Replace all occurrences if True.

    Returns:
        Replacement status.
    """

    try:
        path = get_safe_path(file_path, directory)

        if not path.is_file():
            return f"Error: File not found: {file_path}"

        if not old_text:
            return "Error: old_text cannot be empty."

        content = path.read_text(encoding="utf-8")

        count = content.count(old_text)

        if count == 0:
            return "Error: Target text not found."

        if count > 1 and not replace_all:
            return (
                f"Error: Found {count} matches. "
                "Provide unique old_text or set replace_all=True."
            )

        updated = (
            content.replace(old_text, new_text)
            if replace_all
            else content.replace(old_text, new_text, 1)
        )

        path.write_text(updated, encoding="utf-8")

        return (
            f"Text replaced successfully. "
            f"Replacements: {count if replace_all else 1}"
        )

    except Exception as e:
        return f"Replace error: {e}"


from pathlib import Path


def find_file_location(
    file_name: str,
    case_sensitive: bool = False
) -> list[str]:
    """
    Find all locations of a file by its name in the current directory.

    Args:
        file_name: Name of the file to search.
        case_sensitive: Whether filename matching is case-sensitive.

    Returns:
        List of matching file paths.
    """
    
    try:
        root = Path(directory or "./").resolve()

        if not root.is_dir():
            return []

        if not file_name:
            return []

        results = []

        for path in root.rglob("*"):
            if path.is_symlink() or not path.is_file():
                continue

            if case_sensitive:
                match = path.name == file_name
            else:
                match = path.name.lower() == file_name.lower()

            if match:
                results.append(str(path))

        return sorted(results)

    except Exception:
        return []
