from src.tools.file_tools import (
    read_file,
    edit_file,
    write_file,
    move_file,
    list_files,
    read_file_lines,
    delete_file,
    grep
)
from src.tools.cmd_tools import (
    run_command,
    install_package,
    run_python,
    git
)
from src.tools.web_tools import (
    fetch_url
)
from src.utils.helpers import update_todo


TOOLS = {f.__name__: f for f in (
    write_file, read_file, edit_file, list_files, read_file_lines, grep, delete_file,
    move_file, run_python, install_package, run_command, git, fetch_url, update_todo)}


def _schema(name, desc, props, required):
    return {"type": "function", "function": {
        "name": name, "description": desc,
        "parameters": {"type": "object",
                       "properties": {k: {"type": "string"} for k in props},
                       "required": required}}}


TOOL_SCHEMAS = [
    _schema("write_file", "Create or overwrite a file", ["path", "content"], ["path", "content"]),
    _schema("read_file", "Read a whole file", ["path"], ["path"]),
    _schema("edit_file", "Replace one exact occurrence of text in a file",
            ["path", "old", "new"], ["path", "old", "new"]),
    _schema("list_files", "List all files in the workspace", [], []),
    _schema("read_file_lines", "Read a line range of a file, with line numbers",
            ["path", "start", "end"], ["path", "start", "end"]),
    _schema("grep", "Regex search across workspace files", ["pattern", "path"], ["pattern"]),
    _schema("delete_file", "Delete a file or folder", ["path"], ["path"]),
    _schema("move_file", "Move or rename a file", ["src", "dst"], ["src", "dst"]),
    _schema("run_python", "Run a Python file and return its output", ["path"], ["path"]),
    _schema("install_package", "pip install a Python package", ["package"], ["package"]),
    _schema("run_command", "Run a shell command in the workspace", ["command"], ["command"]),
    _schema("git", "Run git: status, diff, log, show, add, commit, restore, branch",
            ["args"], ["args"]),
    _schema("fetch_url", "Fetch a web page or API response as text", ["url"], ["url"]),
    _schema("update_todo", "Write or update your task checklist (markdown)",
            ["todos"], ["todos"]),
]
