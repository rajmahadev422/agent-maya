import os
import subprocess
import difflib

# local modules
from src.config import (
    WORKDIR,
    YELLOW, GREEN, RED, RESET, DIM, CYAN,
    STATE
)


def update_todo(todos):
    print(f"{CYAN}{todos}{RESET}")
    return "Todo list updated"

def _safe(path):
    full = os.path.abspath(os.path.join(WORKDIR, path))
    if full != WORKDIR and not full.startswith(WORKDIR + os.sep):
        raise ValueError("Path is outside the workspace")
    return full


def confirm(action):
    safe = action.startswith(("apply", "run python"))
    if STATE["auto"] and safe:
        return True
    return input(f"\n  {YELLOW}Allow: {action}? [y/N]{RESET} ").strip().lower() == "y"


def show_diff(path, old, new):
    for line in difflib.unified_diff(old.splitlines(), new.splitlines(),
                                     f"a/{path}", f"b/{path}", lineterm="", n=2):
        if line.startswith("+") and not line.startswith("+++"):
            color = GREEN
        elif line.startswith("-") and not line.startswith("---"):
            color = RED
        else:
            color = DIM
        print(color + line + RESET)


def short(value, n=80):
    s = str(value).replace("\n", "\\n")
    return s if len(s) <= n else s[:n] + "..."


def _run(cmd, shell=False, timeout=60):
    try:
        r = subprocess.run(cmd, shell=shell, cwd=WORKDIR, capture_output=True,
                           text=True, timeout=timeout)
        return (f"exit code {r.returncode}\nstdout:\n{r.stdout[-4000:]}"
                f"\nstderr:\n{r.stderr[-2000:]}")
    except subprocess.TimeoutExpired:
        return f"Error: timed out after {timeout}s"


def _git(*args):
    return subprocess.run(
        ["git", "-c", "user.name=agent", "-c", "user.email=agent@local", *args],
        cwd=WORKDIR, capture_output=True, text=True)
