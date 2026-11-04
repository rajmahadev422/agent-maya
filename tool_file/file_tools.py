import os
import json

def search_files(query: str, directory: str = ".", extension: str = "") -> str:
    """Search for files in a directory matching a text query or extension.
    
    Args:
        query: The search term to look for in file names or contents.
        directory: The root directory to search within (defaults to current directory).
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
        file_path: The path to the file to read.
        
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
        file_path: The path to the file to write.
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


def update_file(file_path: str, content: str, mode: str = "append") -> str:
    """Update an existing file by appending content or overwriting it.
    
    Args:
        file_path: The path to the file to update.
        content: The text content to add or write.
        mode: The update mode, either 'append' (default) to add to the end or 'overwrite'.
        
    Returns:
        A success or error message.
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: File {file_path} does not exist. Use write_file instead."
        
        file_mode = "a" if mode == "append" else "w"
        with open(file_path, file_mode, encoding="utf-8") as f:
            f.write(content)
        return f"Successfully updated {file_path} using mode '{mode}'"
    except Exception as e:
        return f"Error updating file: {str(e)}"


def delete_file(file_path: str) -> str:
    """Delete a file from the file system.
    
    Args:
        file_path: The path to the file to delete.
        
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
    
