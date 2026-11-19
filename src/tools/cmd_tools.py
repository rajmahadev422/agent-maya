import sys
import shlex

# local modules
from src.utils.helpers import (
    _run,
    confirm,
    _git
)
from src.config import BLOCKED

# terminal functions
def run_python(path):
    if not confirm(f"run python {path}"):
        return "User denied"
    return _run([sys.executable, path])


def install_package(package):
    if not confirm(f"pip install {package}"):
        return "User denied"
    return _run([sys.executable, "-m", "pip", "install", package], timeout=300)


def run_command(command):
    if any(b in command for b in BLOCKED):
        return "Error: command blocked"
    if not confirm(f"shell: {command}"):
        return "User denied"
    return _run(command, shell=True, timeout=120)

GIT_ALLOWED = {"status", "diff", "log", "show", "add", "commit", "restore", "branch"}

def git(args):
    parts = shlex.split(args)
    if not parts or parts[0] not in GIT_ALLOWED:
        return f"Error: allowed git subcommands: {sorted(GIT_ALLOWED)}"
    if parts[0] in ("commit", "restore") and not confirm(f"git {args}"):
        return "User denied"
    r = _git(*parts)
    return (r.stdout + r.stderr)[-4000:] or "(no output)"
